import pytest
from eunomia_core import enums, schemas
from sqlalchemy.orm import Session

from eunomia.fetchers.registry import RegistryFetcher, RegistryFetcherConfig
from eunomia.fetchers.registry.db import crud


class TestRegistryFetcher:
    """Test the RegistryFetcher class functionality"""

    def test_init_with_config(
        self,
        registry_fetcher: RegistryFetcher,
        registry_fetcher_config: RegistryFetcherConfig,
    ):
        """Test fetcher initialization with config"""

        assert registry_fetcher.config == registry_fetcher_config
        assert registry_fetcher.config.sql_database_url == "sqlite:///:memory:"

    def test_register_entity_success(
        self,
        fixture_registry_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        registry_fetcher: RegistryFetcher,
    ):
        """Test successful entity registration"""

        result = registry_fetcher.register_entity(
            sample_entity_create_resource, fixture_registry_db
        )
        attributes_dict = {attr.key: attr.value for attr in result.attributes}

        assert isinstance(result, schemas.EntityInDb)
        assert result.uri == sample_entity_create_resource.uri
        assert result.type == sample_entity_create_resource.type
        assert "name" in attributes_dict
        assert attributes_dict["name"] == "Test Resource"

    def test_register_entity_duplicate_uri(
        self,
        fixture_registry_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        registry_fetcher: RegistryFetcher,
    ):
        """Test registering entity with duplicate URI raises error"""

        # Register first entity
        registry_fetcher.register_entity(
            sample_entity_create_resource, fixture_registry_db
        )

        # Try to register same entity again
        with pytest.raises(
            ValueError,
            match="Entity with uri 'test://resource/1' is already registered",
        ):
            registry_fetcher.register_entity(
                sample_entity_create_resource, fixture_registry_db
            )

    def test_register_entity_different_types(
        self, fixture_registry_db: Session, registry_fetcher: RegistryFetcher
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

        resource_result = registry_fetcher.register_entity(
            resource_entity, fixture_registry_db
        )
        principal_result = registry_fetcher.register_entity(
            principal_entity, fixture_registry_db
        )

        assert resource_result.type == enums.EntityType.resource
        assert principal_result.type == enums.EntityType.principal

    def test_update_entity_success(
        self,
        fixture_registry_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        registry_fetcher: RegistryFetcher,
    ):
        """Test successful entity update"""
        # Register initial entity
        registry_fetcher.register_entity(
            sample_entity_create_resource, fixture_registry_db
        )

        # Update entity
        update_data = schemas.EntityUpdate(
            uri="test://resource/1",
            attributes=[
                schemas.Attribute(key="name", value="Updated Resource"),
                schemas.Attribute(key="description", value="New description"),
            ],
        )

        result = registry_fetcher.update_entity(
            update_data, override=False, db=fixture_registry_db
        )
        attributes_dict = {attr.key: attr.value for attr in result.attributes}

        assert attributes_dict["name"] == "Updated Resource"
        assert attributes_dict["description"] == "New description"
        # Should retain original attributes
        assert attributes_dict["type"] == "document"

    def test_update_entity_with_override(
        self,
        fixture_registry_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        registry_fetcher: RegistryFetcher,
    ):
        """Test entity update with override=True"""

        # Register initial entity
        registry_fetcher.register_entity(
            sample_entity_create_resource, fixture_registry_db
        )

        # Update with override
        update_data = schemas.EntityUpdate(
            uri="test://resource/1",
            attributes=[
                schemas.Attribute(key="name", value="Updated Resource"),
                schemas.Attribute(key="description", value="New description"),
            ],
        )

        result = registry_fetcher.update_entity(
            update_data, override=True, db=fixture_registry_db
        )
        attributes_dict = {attr.key: attr.value for attr in result.attributes}

        assert attributes_dict["name"] == "Updated Resource"
        assert attributes_dict["description"] == "New description"
        # Should NOT retain original attributes
        assert "type" not in attributes_dict
        assert "owner" not in attributes_dict

    def test_update_entity_not_found(
        self, fixture_registry_db: Session, registry_fetcher: RegistryFetcher
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
            registry_fetcher.update_entity(
                update_data, override=False, db=fixture_registry_db
            )

    def test_delete_entity_success(
        self,
        fixture_registry_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        registry_fetcher: RegistryFetcher,
    ):
        """Test successful entity deletion"""

        # Register entity
        registry_fetcher.register_entity(
            sample_entity_create_resource, fixture_registry_db
        )

        # Verify entity exists
        assert crud.get_entity("test://resource/1", fixture_registry_db) is not None

        # Delete entity
        registry_fetcher.delete_entity("test://resource/1", fixture_registry_db)

        # Verify entity is deleted
        assert crud.get_entity("test://resource/1", fixture_registry_db) is None

    def test_delete_entity_not_found(
        self, fixture_registry_db: Session, registry_fetcher: RegistryFetcher
    ):
        """Test deleting non-existent entity raises error"""

        with pytest.raises(
            ValueError,
            match="Entity with uri 'test://resource/nonexistent' is not registered",
        ):
            registry_fetcher.delete_entity(
                "test://resource/nonexistent", fixture_registry_db
            )

    @pytest.mark.asyncio
    async def test_fetch_attributes_success(
        self,
        fixture_registry_db: Session,
        sample_entity_create_resource: schemas.EntityCreate,
        registry_fetcher: RegistryFetcher,
    ):
        """Test successful attribute fetching"""

        # Register entity
        registry_fetcher.register_entity(
            sample_entity_create_resource, fixture_registry_db
        )

        # Fetch attributes
        attributes = await registry_fetcher.fetch_attributes("test://resource/1")

        assert isinstance(attributes, dict)
        assert "name" in attributes
        assert attributes["name"] == "Test Resource"
        assert "type" in attributes
        assert attributes["type"] == "document"
        assert "owner" in attributes
        assert attributes["owner"] == "user123"

    @pytest.mark.asyncio
    async def test_fetch_attributes_not_found(
        self, fixture_registry_db: Session, registry_fetcher: RegistryFetcher
    ):
        """Test fetching attributes for non-existent entity"""

        # Fetch attributes for non-existent entity
        attributes = await registry_fetcher.fetch_attributes(
            "test://resource/nonexistent"
        )

        assert attributes == {}

    def test_entity_lifecycle(
        self, fixture_registry_db: Session, registry_fetcher: RegistryFetcher
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

        created = registry_fetcher.register_entity(entity, fixture_registry_db)
        attributes_dict = {attr.key: attr.value for attr in created.attributes}
        assert created.uri == "test://resource/lifecycle"
        assert attributes_dict["name"] == "Lifecycle Test"

        # Update entity
        update = schemas.EntityUpdate(
            uri="test://resource/lifecycle",
            attributes=[
                schemas.Attribute(key="version", value="v2.0"),
                schemas.Attribute(key="status", value="active"),
            ],
        )

        updated = registry_fetcher.update_entity(
            update, override=False, db=fixture_registry_db
        )
        attributes_dict = {attr.key: attr.value for attr in updated.attributes}
        assert attributes_dict["version"] == "v2.0"
        assert attributes_dict["status"] == "active"
        assert attributes_dict["name"] == "Lifecycle Test"  # Should retain

        # Delete entity
        registry_fetcher.delete_entity("test://resource/lifecycle", fixture_registry_db)

        # Verify deletion
        with pytest.raises(
            ValueError,
            match="Entity with uri 'test://resource/lifecycle' is not registered",
        ):
            registry_fetcher.delete_entity(
                "test://resource/lifecycle", fixture_registry_db
            )

    def test_complex_attribute_types(
        self, fixture_registry_db: Session, registry_fetcher: RegistryFetcher
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

        created = registry_fetcher.register_entity(entity, fixture_registry_db)
        attributes_dict = {attr.key: attr.value for attr in created.attributes}

        assert attributes_dict["name"] == "Complex Entity"
        assert attributes_dict["tags"] == ["tag1", "tag2", "tag3"]
        assert attributes_dict["metadata"] == {
            "key": "value",
            "nested": {"inner": "data"},
        }
        assert attributes_dict["score"] == 42.5
        assert attributes_dict["active"] is True
