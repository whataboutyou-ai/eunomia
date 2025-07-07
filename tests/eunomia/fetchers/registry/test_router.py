import pytest
from unittest.mock import Mock, patch
from fastapi import status
from fastapi.testclient import TestClient
from fastapi import FastAPI
from eunomia_core import enums, schemas
from sqlalchemy.orm import Session

from eunomia.fetchers.registry import RegistryFetcher, RegistryFetcherConfig
from eunomia.fetchers.registry.router import registry_router_factory
from eunomia.fetchers.registry.db import crud


class TestRegistryRouter:
    """Test the registry router functionality"""

    @pytest.fixture
    def app_with_router(self, fixture_registry_db: Session):
        """Create FastAPI app with registry router"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        router = registry_router_factory(fetcher)
        
        app = FastAPI()
        app.include_router(router, prefix="/registry")
        
        # Mock the get_db dependency
        def override_get_db():
            yield fixture_registry_db
        
        from eunomia.fetchers.registry.db import db
        app.dependency_overrides[db.get_db] = override_get_db
        
        return app

    @pytest.fixture
    def client(self, app_with_router):
        """Create test client"""
        return TestClient(app_with_router)

    def test_get_entities_empty(self, client: TestClient):
        """Test getting entities when database is empty"""
        response = client.get("/registry/entities")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_entities_with_pagination(self, client: TestClient, setup_test_entities):
        """Test getting entities with pagination"""
        # Test default pagination
        response = client.get("/registry/entities")
        
        assert response.status_code == status.HTTP_200_OK
        entities = response.json()
        assert len(entities) == 3  # We have 3 entities in setup
        
        # Test with limit
        response = client.get("/registry/entities?limit=2")
        assert response.status_code == status.HTTP_200_OK
        entities = response.json()
        assert len(entities) == 2
        
        # Test with offset
        response = client.get("/registry/entities?offset=1&limit=2")
        assert response.status_code == status.HTTP_200_OK
        entities = response.json()
        assert len(entities) == 2

    def test_get_entities_structure(self, client: TestClient, setup_test_entities):
        """Test the structure of returned entities"""
        response = client.get("/registry/entities")
        
        assert response.status_code == status.HTTP_200_OK
        entities = response.json()
        
        for entity in entities:
            assert "uri" in entity
            assert "type" in entity
            assert "attributes" in entity
            assert isinstance(entity["attributes"], dict)

    def test_get_entities_count_empty(self, client: TestClient):
        """Test getting entity count when database is empty"""
        response = client.get("/registry/entities/$count")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == 0

    def test_get_entities_count_with_data(self, client: TestClient, setup_test_entities):
        """Test getting entity count with data"""
        response = client.get("/registry/entities/$count")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == 3

    def test_create_entity_success(self, client: TestClient, sample_entity_create_resource: schemas.EntityCreate):
        """Test successful entity creation"""
        entity_data = sample_entity_create_resource.model_dump()
        
        response = client.post("/registry/entities", json=entity_data)
        
        assert response.status_code == status.HTTP_200_OK
        created_entity = response.json()
        
        assert created_entity["uri"] == sample_entity_create_resource.uri
        assert created_entity["type"] == sample_entity_create_resource.type.value
        assert "name" in created_entity["attributes"]
        assert created_entity["attributes"]["name"] == "Test Resource"

    def test_create_entity_duplicate_uri(self, client: TestClient, sample_entity_create_resource: schemas.EntityCreate):
        """Test creating entity with duplicate URI"""
        entity_data = sample_entity_create_resource.model_dump()
        
        # Create first entity
        response = client.post("/registry/entities", json=entity_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Try to create same entity again
        response = client.post("/registry/entities", json=entity_data)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_create_entity_invalid_data(self, client: TestClient):
        """Test creating entity with invalid data"""
        invalid_data = {
            "uri": "test://resource/invalid",
            "type": "invalid_type",
            "attributes": []
        }
        
        response = client.post("/registry/entities", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_entity_missing_required_fields(self, client: TestClient):
        """Test creating entity with missing required fields"""
        incomplete_data = {
            "uri": "test://resource/incomplete"
        }
        
        response = client.post("/registry/entities", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_entity_success(self, client: TestClient, sample_entity_create_resource: schemas.EntityCreate):
        """Test successful entity retrieval"""
        # Create entity first
        entity_data = sample_entity_create_resource.model_dump()
        client.post("/registry/entities", json=entity_data)
        
        # Get the entity
        response = client.get(f"/registry/entities/{sample_entity_create_resource.uri}")
        
        assert response.status_code == status.HTTP_200_OK
        entity = response.json()
        
        assert entity["uri"] == sample_entity_create_resource.uri
        assert entity["type"] == sample_entity_create_resource.type.value
        assert "name" in entity["attributes"]

    def test_get_entity_not_found(self, client: TestClient):
        """Test getting non-existent entity"""
        response = client.get("/registry/entities/test://resource/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Entity not found"

    def test_get_entity_with_special_characters(self, client: TestClient):
        """Test getting entity with special characters in URI"""
        # Create entity with special characters
        entity_data = {
            "uri": "test://resource/special-chars_123",
            "type": "resource",
            "attributes": [{"key": "name", "value": "Special Entity"}]
        }
        
        response = client.post("/registry/entities", json=entity_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Get the entity
        response = client.get("/registry/entities/test://resource/special-chars_123")
        assert response.status_code == status.HTTP_200_OK

    def test_update_entity_success(self, client: TestClient, sample_entity_create_resource: schemas.EntityCreate):
        """Test successful entity update"""
        # Create entity first
        entity_data = sample_entity_create_resource.model_dump()
        client.post("/registry/entities", json=entity_data)
        
        # Update the entity
        update_data = {
            "uri": sample_entity_create_resource.uri,
            "attributes": [
                {"key": "name", "value": "Updated Resource"},
                {"key": "description", "value": "Updated description"}
            ]
        }
        
        response = client.put(f"/registry/entities/{sample_entity_create_resource.uri}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        updated_entity = response.json()
        
        assert updated_entity["attributes"]["name"] == "Updated Resource"
        assert updated_entity["attributes"]["description"] == "Updated description"

    def test_update_entity_with_override(self, client: TestClient, sample_entity_create_resource: schemas.EntityCreate):
        """Test entity update with override parameter"""
        # Create entity first
        entity_data = sample_entity_create_resource.model_dump()
        client.post("/registry/entities", json=entity_data)
        
        # Update with override
        update_data = {
            "uri": sample_entity_create_resource.uri,
            "attributes": [
                {"key": "name", "value": "Updated Resource"},
                {"key": "description", "value": "New description"}
            ]
        }
        
        response = client.put(
            f"/registry/entities/{sample_entity_create_resource.uri}?override=true",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        updated_entity = response.json()
        
        assert updated_entity["attributes"]["name"] == "Updated Resource"
        assert updated_entity["attributes"]["description"] == "New description"

    def test_update_entity_uri_mismatch(self, client: TestClient, sample_entity_create_resource: schemas.EntityCreate):
        """Test updating entity with URI mismatch"""
        # Create entity first
        entity_data = sample_entity_create_resource.model_dump()
        client.post("/registry/entities", json=entity_data)
        
        # Try to update with different URI
        update_data = {
            "uri": "test://resource/different",
            "attributes": [{"key": "name", "value": "Updated"}]
        }
        
        response = client.put(f"/registry/entities/{sample_entity_create_resource.uri}", json=update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "URI mismatch"

    def test_update_entity_not_found(self, client: TestClient):
        """Test updating non-existent entity"""
        update_data = {
            "uri": "test://resource/nonexistent",
            "attributes": [{"key": "name", "value": "Updated"}]
        }
        
        response = client.put("/registry/entities/test://resource/nonexistent", json=update_data)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_delete_entity_success(self, client: TestClient, sample_entity_create_resource: schemas.EntityCreate):
        """Test successful entity deletion"""
        # Create entity first
        entity_data = sample_entity_create_resource.model_dump()
        client.post("/registry/entities", json=entity_data)
        
        # Delete the entity
        response = client.delete(f"/registry/entities/{sample_entity_create_resource.uri}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is True
        
        # Verify entity is deleted
        response = client.get(f"/registry/entities/{sample_entity_create_resource.uri}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_entity_not_found(self, client: TestClient):
        """Test deleting non-existent entity"""
        response = client.delete("/registry/entities/test://resource/nonexistent")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_router_dependency_injection(self, fixture_registry_db: Session):
        """Test that router properly uses dependency injection"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        router = registry_router_factory(fetcher)
        
        # Verify router was created
        assert router is not None
        assert hasattr(router, 'routes')
        assert len(router.routes) > 0

    def test_router_endpoints_exist(self, fixture_registry_db: Session):
        """Test that all expected router endpoints exist"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        router = registry_router_factory(fetcher)
        
        # Check that all expected routes are present
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/entities",
            "/entities/$count",
            "/entities/{uri}",
        ]
        
        for expected_route in expected_routes:
            assert any(expected_route in route for route in routes)

    def test_crud_operations_integration(self, client: TestClient):
        """Test complete CRUD operations through the router"""
        # Create
        entity_data = {
            "uri": "test://resource/crud",
            "type": "resource",
            "attributes": [
                {"key": "name", "value": "CRUD Test"},
                {"key": "version", "value": "1.0"}
            ]
        }
        
        response = client.post("/registry/entities", json=entity_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Read
        response = client.get("/registry/entities/test://resource/crud")
        assert response.status_code == status.HTTP_200_OK
        entity = response.json()
        assert entity["attributes"]["name"] == "CRUD Test"
        
        # Update
        update_data = {
            "uri": "test://resource/crud",
            "attributes": [
                {"key": "name", "value": "Updated CRUD Test"},
                {"key": "version", "value": "2.0"}
            ]
        }
        
        response = client.put("/registry/entities/test://resource/crud", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify update
        response = client.get("/registry/entities/test://resource/crud")
        assert response.status_code == status.HTTP_200_OK
        entity = response.json()
        assert entity["attributes"]["name"] == "Updated CRUD Test"
        assert entity["attributes"]["version"] == "2.0"
        
        # Delete
        response = client.delete("/registry/entities/test://resource/crud")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify deletion
        response = client.get("/registry/entities/test://resource/crud")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_router_error_handling(self, client: TestClient):
        """Test router error handling for various scenarios"""
        # Test invalid JSON
        response = client.post("/registry/entities", content="invalid json")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test missing content type
        response = client.post("/registry/entities", data="some data")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test method not allowed
        response = client.patch("/registry/entities")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_router_with_complex_entities(self, client: TestClient):
        """Test router with complex entity structures"""
        entity_data = {
            "uri": "test://resource/complex",
            "type": "resource",
            "attributes": [
                {"key": "name", "value": "Complex Entity"},
                {"key": "metadata", "value": {"nested": {"key": "value"}}},
                {"key": "tags", "value": ["tag1", "tag2", "tag3"]},
                {"key": "score", "value": 42.5},
                {"key": "active", "value": True}
            ]
        }
        
        # Create complex entity
        response = client.post("/registry/entities", json=entity_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Retrieve and verify
        response = client.get("/registry/entities/test://resource/complex")
        assert response.status_code == status.HTTP_200_OK
        entity = response.json()
        
        assert entity["attributes"]["name"] == "Complex Entity"
        assert entity["attributes"]["metadata"] == {"nested": {"key": "value"}}
        assert entity["attributes"]["tags"] == ["tag1", "tag2", "tag3"]
        assert entity["attributes"]["score"] == 42.5
        assert entity["attributes"]["active"] is True