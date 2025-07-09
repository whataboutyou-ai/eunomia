import pytest
from eunomia_core import enums, schemas
from sqlalchemy.orm import Session

from eunomia.fetchers.registry import RegistryFetcher, RegistryFetcherConfig
from eunomia.fetchers.registry.db import crud


class TestRegistryFetcher:
    """Test the RegistryFetcher class functionality"""

    def test_init_with_config(
        self,
        fixture_registry: RegistryFetcher,
        fixture_registry_config: RegistryFetcherConfig,
    ):
        """Test fetcher initialization with config"""

        assert fixture_registry.config == fixture_registry_config
        assert fixture_registry.config.sql_database_url == "sqlite:///:memory:"

    def test_register_entity_success(
        self,
        fixture_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        fixture_registry: RegistryFetcher,
    ):
        """Test successful entity registration"""

        result = fixture_registry.register_entity(
            sample_entity_create_resource, fixture_db
        )

        assert isinstance(result, schemas.EntityInDb)
        assert result.uri == sample_entity_create_resource.uri
        assert result.type == sample_entity_create_resource.type
        assert "name" in result.attributes_dict
        assert result.attributes_dict["name"] == "Test Resource"

    def test_register_entity_duplicate_uri(
        self,
        fixture_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        fixture_registry: RegistryFetcher,
    ):
        """Test registering entity with duplicate URI raises error"""

        # Register first entity
        fixture_registry.register_entity(sample_entity_create_resource, fixture_db)

        # Try to register same entity again
        with pytest.raises(
            ValueError,
            match="Entity with uri 'test://resource/1' is already registered",
        ):
            fixture_registry.register_entity(sample_entity_create_resource, fixture_db)

    def test_register_entity_different_types(
        self, fixture_db: Session, fixture_registry: RegistryFetcher
    ):
        """Test registering entities of different types"""

        resource_entity = schemas.EntityCreate(
            uri="test://resource/1",
            type=enums.EntityType.resource,
            attributes=[schemas.Attribute(key="name", value="Resource")],
        )

        principal_entity = schemas.EntityCreate(
            uri="test://principal/1",
            type=enums.EntityType.principal,
            attributes=[schemas.Attribute(key="name", value="Principal")],
        )

        resource_result = fixture_registry.register_entity(resource_entity, fixture_db)
        principal_result = fixture_registry.register_entity(
            principal_entity, fixture_db
        )

        assert resource_result.type == enums.EntityType.resource
        assert principal_result.type == enums.EntityType.principal

    def test_update_entity_success(
        self,
        fixture_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        fixture_registry: RegistryFetcher,
    ):
        """Test successful entity update"""
        # Register initial entity
        fixture_registry.register_entity(sample_entity_create_resource, fixture_db)

        # Update entity
        update_data = schemas.EntityUpdate(
            uri="test://resource/1",
            attributes=[
                schemas.Attribute(key="name", value="Updated Resource"),
                schemas.Attribute(key="description", value="New description"),
            ],
        )

        result = fixture_registry.update_entity(
            update_data, override=False, db_session=fixture_db
        )

        assert result.attributes_dict["name"] == "Updated Resource"
        assert result.attributes_dict["description"] == "New description"
        # Should retain original attributes
        assert result.attributes_dict["type"] == "document"

    def test_update_entity_with_override(
        self,
        fixture_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        fixture_registry: RegistryFetcher,
    ):
        """Test entity update with override=True"""

        # Register initial entity
        fixture_registry.register_entity(sample_entity_create_resource, fixture_db)

        # Update with override
        update_data = schemas.EntityUpdate(
            uri="test://resource/1",
            attributes=[
                schemas.Attribute(key="name", value="Updated Resource"),
                schemas.Attribute(key="description", value="New description"),
            ],
        )

        result = fixture_registry.update_entity(
            update_data, override=True, db_session=fixture_db
        )

        assert result.attributes_dict["name"] == "Updated Resource"
        assert result.attributes_dict["description"] == "New description"
        # Should NOT retain original attributes
        assert "type" not in result.attributes_dict
        assert "owner" not in result.attributes_dict

    def test_update_entity_not_found(
        self, fixture_db: Session, fixture_registry: RegistryFetcher
    ):
        """Test updating non-existent entity raises error"""

        update_data = schemas.EntityUpdate(
            uri="test://resource/nonexistent",
            attributes=[schemas.Attribute(key="name", value="Updated")],
        )

        with pytest.raises(
            ValueError,
            match="Entity with uri 'test://resource/nonexistent' is not registered",
        ):
            fixture_registry.update_entity(
                update_data, override=False, db_session=fixture_db
            )

    def test_delete_entity_success(
        self,
        fixture_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        fixture_registry: RegistryFetcher,
    ):
        """Test successful entity deletion"""

        # Register entity
        fixture_registry.register_entity(sample_entity_create_resource, fixture_db)

        # Verify entity exists
        assert crud.get_entity("test://resource/1", fixture_db) is not None

        # Delete entity
        fixture_registry.delete_entity("test://resource/1", fixture_db)

        # Verify entity is deleted
        assert crud.get_entity("test://resource/1", fixture_db) is None

    def test_delete_entity_not_found(
        self, fixture_db: Session, fixture_registry: RegistryFetcher
    ):
        """Test deleting non-existent entity raises error"""

        with pytest.raises(
            ValueError,
            match="Entity with uri 'test://resource/nonexistent' is not registered",
        ):
            fixture_registry.delete_entity("test://resource/nonexistent", fixture_db)

    @pytest.mark.asyncio
    async def test_fetch_attributes_success(
        self, fixture_registry_with_entity: RegistryFetcher
    ):
        """Test successful attribute fetching"""

        # Fetch attributes
        attributes = await fixture_registry_with_entity.fetch_attributes(
            "test://resource/1"
        )

        assert isinstance(attributes, dict)
        assert "name" in attributes
        assert attributes["name"] == "Test Resource"
        assert "type" in attributes
        assert attributes["type"] == "document"
        assert "owner" in attributes
        assert attributes["owner"] == "user123"

    @pytest.mark.asyncio
    async def test_fetch_attributes_not_found(
        self, fixture_registry_with_entity: RegistryFetcher
    ):
        """Test fetching attributes for non-existent entity"""

        # Fetch attributes for non-existent entity
        attributes = await fixture_registry_with_entity.fetch_attributes(
            "test://resource/nonexistent"
        )

        assert attributes == {}

    def test_entity_lifecycle(
        self, fixture_db: Session, fixture_registry: RegistryFetcher
    ):
        """Test complete entity lifecycle: create, update, delete"""

        # Create entity
        entity = schemas.EntityCreate(
            uri="test://resource/lifecycle",
            type=enums.EntityType.resource,
            attributes=[
                schemas.Attribute(key="name", value="Lifecycle Test"),
                schemas.Attribute(key="version", value="v1.0"),
            ],
        )

        created = fixture_registry.register_entity(entity, fixture_db)

        assert created.uri == "test://resource/lifecycle"
        assert created.attributes_dict["name"] == "Lifecycle Test"

        # Update entity
        update = schemas.EntityUpdate(
            uri="test://resource/lifecycle",
            attributes=[
                schemas.Attribute(key="version", value="v2.0"),
                schemas.Attribute(key="status", value="active"),
            ],
        )

        updated = fixture_registry.update_entity(
            update, override=False, db_session=fixture_db
        )

        assert updated.attributes_dict["version"] == "v2.0"
        assert updated.attributes_dict["status"] == "active"
        assert updated.attributes_dict["name"] == "Lifecycle Test"  # Should retain

        # Delete entity
        fixture_registry.delete_entity("test://resource/lifecycle", fixture_db)

        # Verify deletion
        with pytest.raises(
            ValueError,
            match="Entity with uri 'test://resource/lifecycle' is not registered",
        ):
            fixture_registry.delete_entity("test://resource/lifecycle", fixture_db)

    def test_complex_attribute_types(
        self, fixture_db: Session, fixture_registry: RegistryFetcher
    ):
        """Test entities with complex attribute types"""

        # Entity with various attribute types
        entity = schemas.EntityCreate(
            uri="test://resource/complex",
            type=enums.EntityType.resource,
            attributes=[
                schemas.Attribute(key="name", value="Complex Entity"),
                schemas.Attribute(key="tags", value=["tag1", "tag2", "tag3"]),
                schemas.Attribute(
                    key="metadata", value={"key": "value", "nested": {"inner": "data"}}
                ),
                schemas.Attribute(key="score", value=42.5),
                schemas.Attribute(key="active", value=True),
            ],
        )

        created = fixture_registry.register_entity(entity, fixture_db)

        assert created.attributes_dict["name"] == "Complex Entity"
        assert created.attributes_dict["tags"] == ["tag1", "tag2", "tag3"]
        assert created.attributes_dict["metadata"] == {
            "key": "value",
            "nested": {"inner": "data"},
        }
        assert created.attributes_dict["score"] == 42.5
        assert created.attributes_dict["active"] is True
