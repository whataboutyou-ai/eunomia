import pytest
from eunomia_core import enums, schemas
from sqlalchemy.orm import Session

from eunomia.fetchers.registry import RegistryFetcher, RegistryFetcherConfig
from eunomia.fetchers.registry.db import crud


class TestRegistryFetcher:
    """Test the RegistryFetcher class functionality"""

    def test_init_with_config(self):
        """Test fetcher initialization with config"""
        config = RegistryFetcherConfig(
            sql_database_url="sqlite:///:memory:",
            entity_type=enums.EntityType.resource
        )
        fetcher = RegistryFetcher(config)
        
        assert fetcher.config == config
        assert fetcher.config.sql_database_url == "sqlite:///:memory:"
        assert fetcher.config.entity_type == enums.EntityType.resource

    def test_register_entity_success(self, fixture_registry_db: Session, sample_entity_create_resource: schemas.EntityCreate):
        """Test successful entity registration"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        result = fetcher.register_entity(sample_entity_create_resource, fixture_registry_db)
        
        assert isinstance(result, schemas.EntityInDb)
        assert result.uri == sample_entity_create_resource.uri
        assert result.type == sample_entity_create_resource.type
        assert "name" in result.attributes
        assert result.attributes["name"] == "Test Resource"

    def test_register_entity_duplicate_uri(self, fixture_registry_db: Session, sample_entity_create_resource: schemas.EntityCreate):
        """Test registering entity with duplicate URI raises error"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        # Register first entity
        fetcher.register_entity(sample_entity_create_resource, fixture_registry_db)
        
        # Try to register same entity again
        with pytest.raises(ValueError, match="Entity with uri 'test://resource/1' is already registered"):
            fetcher.register_entity(sample_entity_create_resource, fixture_registry_db)

    def test_register_entity_different_types(self, fixture_registry_db: Session):
        """Test registering entities of different types"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        resource_entity = schemas.EntityCreate(
            uri="test://resource/1",
            type=enums.EntityType.resource,
            attributes=[schemas.Attribute(key="name", value="Resource")]
        )
        
        principal_entity = schemas.EntityCreate(
            uri="test://principal/1",
            type=enums.EntityType.principal,
            attributes=[schemas.Attribute(key="name", value="Principal")]
        )
        
        resource_result = fetcher.register_entity(resource_entity, fixture_registry_db)
        principal_result = fetcher.register_entity(principal_entity, fixture_registry_db)
        
        assert resource_result.type == enums.EntityType.resource
        assert principal_result.type == enums.EntityType.principal

    def test_update_entity_success(self, fixture_registry_db: Session, sample_entity_create_resource: schemas.EntityCreate):
        """Test successful entity update"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        # Register initial entity
        fetcher.register_entity(sample_entity_create_resource, fixture_registry_db)
        
        # Update entity
        update_data = schemas.EntityUpdate(
            uri="test://resource/1",
            attributes=[
                schemas.Attribute(key="name", value="Updated Resource"),
                schemas.Attribute(key="description", value="New description"),
            ]
        )
        
        result = fetcher.update_entity(update_data, override=False, db=fixture_registry_db)
        
        assert result.attributes["name"] == "Updated Resource"
        assert result.attributes["description"] == "New description"
        # Should retain original attributes
        assert result.attributes["type"] == "document"

    def test_update_entity_with_override(self, fixture_registry_db: Session, sample_entity_create_resource: schemas.EntityCreate):
        """Test entity update with override=True"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        # Register initial entity
        fetcher.register_entity(sample_entity_create_resource, fixture_registry_db)
        
        # Update with override
        update_data = schemas.EntityUpdate(
            uri="test://resource/1",
            attributes=[
                schemas.Attribute(key="name", value="Updated Resource"),
                schemas.Attribute(key="description", value="New description"),
            ]
        )
        
        result = fetcher.update_entity(update_data, override=True, db=fixture_registry_db)
        
        assert result.attributes["name"] == "Updated Resource"
        assert result.attributes["description"] == "New description"
        # Should NOT retain original attributes
        assert "type" not in result.attributes
        assert "owner" not in result.attributes

    def test_update_entity_not_found(self, fixture_registry_db: Session):
        """Test updating non-existent entity raises error"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        update_data = schemas.EntityUpdate(
            uri="test://resource/nonexistent",
            attributes=[schemas.Attribute(key="name", value="Updated")]
        )
        
        with pytest.raises(ValueError, match="Entity with uri 'test://resource/nonexistent' is not registered"):
            fetcher.update_entity(update_data, override=False, db=fixture_registry_db)

    def test_delete_entity_success(self, fixture_registry_db: Session, sample_entity_create_resource: schemas.EntityCreate):
        """Test successful entity deletion"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        # Register entity
        fetcher.register_entity(sample_entity_create_resource, fixture_registry_db)
        
        # Verify entity exists
        assert crud.get_entity("test://resource/1", fixture_registry_db) is not None
        
        # Delete entity
        fetcher.delete_entity("test://resource/1", fixture_registry_db)
        
        # Verify entity is deleted
        assert crud.get_entity("test://resource/1", fixture_registry_db) is None

    def test_delete_entity_not_found(self, fixture_registry_db: Session):
        """Test deleting non-existent entity raises error"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        with pytest.raises(ValueError, match="Entity with uri 'test://resource/nonexistent' is not registered"):
            fetcher.delete_entity("test://resource/nonexistent", fixture_registry_db)

    @pytest.mark.asyncio
    async def test_fetch_attributes_success(self, fixture_registry_db: Session, sample_entity_create_resource: schemas.EntityCreate):
        """Test successful attribute fetching"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        # Register entity
        fetcher.register_entity(sample_entity_create_resource, fixture_registry_db)
        
        # Fetch attributes
        attributes = await fetcher.fetch_attributes("test://resource/1")
        
        assert isinstance(attributes, dict)
        assert attributes["name"] == "Test Resource"
        assert attributes["type"] == "document"
        assert attributes["owner"] == "user123"

    @pytest.mark.asyncio
    async def test_fetch_attributes_not_found(self, fixture_registry_db: Session):
        """Test fetching attributes for non-existent entity"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        # Fetch attributes for non-existent entity
        attributes = await fetcher.fetch_attributes("test://resource/nonexistent")
        
        assert attributes == {}

    @pytest.mark.asyncio
    async def test_fetch_attributes_empty_attributes(self, fixture_registry_db: Session):
        """Test fetching attributes for entity with no attributes"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        # Register entity without attributes
        entity = schemas.EntityCreate(
            uri="test://resource/empty",
            type=enums.EntityType.resource,
            attributes=[]
        )
        fetcher.register_entity(entity, fixture_registry_db)
        
        # Fetch attributes
        attributes = await fetcher.fetch_attributes("test://resource/empty")
        
        assert attributes == {}

    def test_entity_lifecycle(self, fixture_registry_db: Session):
        """Test complete entity lifecycle: create, update, delete"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        # Create entity
        entity = schemas.EntityCreate(
            uri="test://resource/lifecycle",
            type=enums.EntityType.resource,
            attributes=[
                schemas.Attribute(key="name", value="Lifecycle Test"),
                schemas.Attribute(key="version", value="1.0"),
            ]
        )
        
        created = fetcher.register_entity(entity, fixture_registry_db)
        assert created.uri == "test://resource/lifecycle"
        assert created.attributes["name"] == "Lifecycle Test"
        
        # Update entity
        update = schemas.EntityUpdate(
            uri="test://resource/lifecycle",
            attributes=[
                schemas.Attribute(key="version", value="2.0"),
                schemas.Attribute(key="status", value="active"),
            ]
        )
        
        updated = fetcher.update_entity(update, override=False, db=fixture_registry_db)
        assert updated.attributes["version"] == "2.0"
        assert updated.attributes["status"] == "active"
        assert updated.attributes["name"] == "Lifecycle Test"  # Should retain
        
        # Delete entity
        fetcher.delete_entity("test://resource/lifecycle", fixture_registry_db)
        
        # Verify deletion
        with pytest.raises(ValueError, match="Entity with uri 'test://resource/lifecycle' is not registered"):
            fetcher.delete_entity("test://resource/lifecycle", fixture_registry_db)

    def test_complex_attribute_types(self, fixture_registry_db: Session):
        """Test entities with complex attribute types"""
        config = RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")
        fetcher = RegistryFetcher(config)
        
        # Entity with various attribute types
        entity = schemas.EntityCreate(
            uri="test://resource/complex",
            type=enums.EntityType.resource,
            attributes=[
                schemas.Attribute(key="name", value="Complex Entity"),
                schemas.Attribute(key="tags", value=["tag1", "tag2", "tag3"]),
                schemas.Attribute(key="metadata", value={"key": "value", "nested": {"inner": "data"}}),
                schemas.Attribute(key="score", value=42.5),
                schemas.Attribute(key="active", value=True),
            ]
        )
        
        created = fetcher.register_entity(entity, fixture_registry_db)
        
        assert created.attributes["name"] == "Complex Entity"
        assert created.attributes["tags"] == ["tag1", "tag2", "tag3"]
        assert created.attributes["metadata"] == {"key": "value", "nested": {"inner": "data"}}
        assert created.attributes["score"] == 42.5
        assert created.attributes["active"] is True