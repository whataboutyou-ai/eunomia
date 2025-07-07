import pytest
from eunomia_core import enums, schemas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eunomia.fetchers.registry import RegistryFetcher, RegistryFetcherConfig
from eunomia.fetchers.registry.db import db


@pytest.fixture(scope="function")
def fixture_registry_db():
    """Create an in-memory SQLite database for registry testing."""
    test_engine = create_engine("sqlite:///:memory:")
    db.Base.metadata.create_all(test_engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    # Override global variables in the db module
    original_engine = db.engine
    original_session_local = db.SessionLocal
    db.engine = test_engine
    db.SessionLocal = TestingSessionLocal

    # Yield a session for the test
    with TestingSessionLocal() as session:
        yield session

    # Clean up after the test
    db.Base.metadata.drop_all(test_engine)

    # Restore original values
    db.engine = original_engine
    db.SessionLocal = original_session_local


@pytest.fixture
def registry_fetcher_config():
    """Create a registry fetcher configuration for testing."""
    return RegistryFetcherConfig(
        sql_database_url="sqlite:///:memory:",
        entity_type=enums.EntityType.resource
    )


@pytest.fixture
def registry_fetcher(registry_fetcher_config):
    """Create a registry fetcher instance for testing."""
    return RegistryFetcher(registry_fetcher_config)


@pytest.fixture
def sample_entity_create_resource():
    """Create a sample resource entity for testing."""
    return schemas.EntityCreate(
        uri="test://resource/1",
        type=enums.EntityType.resource,
        attributes=[
            schemas.Attribute(key="name", value="Test Resource"),
            schemas.Attribute(key="type", value="document"),
            schemas.Attribute(key="owner", value="user123"),
            schemas.Attribute(key="tags", value=["public", "documentation"]),
        ]
    )


@pytest.fixture
def sample_entity_create_principal():
    """Create a sample principal entity for testing."""
    return schemas.EntityCreate(
        uri="test://principal/1",
        type=enums.EntityType.principal,
        attributes=[
            schemas.Attribute(key="name", value="Test User"),
            schemas.Attribute(key="role", value="admin"),
            schemas.Attribute(key="department", value="engineering"),
            schemas.Attribute(key="permissions", value=["read", "write", "delete"]),
        ]
    )


@pytest.fixture
def sample_entity_update_resource():
    """Create a sample entity update for testing."""
    return schemas.EntityUpdate(
        uri="test://resource/1",
        attributes=[
            schemas.Attribute(key="name", value="Updated Test Resource"),
            schemas.Attribute(key="description", value="Updated description"),
            schemas.Attribute(key="version", value="2.0"),
        ]
    )


@pytest.fixture
def multiple_entities():
    """Create multiple sample entities for testing."""
    return [
        schemas.EntityCreate(
            uri="test://resource/1",
            type=enums.EntityType.resource,
            attributes=[schemas.Attribute(key="name", value="Resource 1")]
        ),
        schemas.EntityCreate(
            uri="test://resource/2",
            type=enums.EntityType.resource,
            attributes=[schemas.Attribute(key="name", value="Resource 2")]
        ),
        schemas.EntityCreate(
            uri="test://principal/1",
            type=enums.EntityType.principal,
            attributes=[schemas.Attribute(key="name", value="Principal 1")]
        ),
    ]


@pytest.fixture
def setup_test_entities(fixture_registry_db, multiple_entities):
    """Set up test entities in the database."""
    from eunomia.fetchers.registry.db import crud
    
    created_entities = []
    for entity in multiple_entities:
        db_entity = crud.create_entity(entity, fixture_registry_db)
        created_entities.append(db_entity)
    
    return created_entities