import pytest
from eunomia_core import enums, schemas
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from eunomia.fetchers.registry import RegistryFetcher, RegistryFetcherConfig
from eunomia.fetchers.registry.db import db


@pytest.fixture(scope="function")
def fixture_db():
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
def fixture_registry_config():
    """Create a registry fetcher configuration for testing."""
    return RegistryFetcherConfig(sql_database_url="sqlite:///:memory:")


@pytest.fixture
def fixture_registry(fixture_registry_config):
    """Create a registry fetcher instance for testing."""
    return RegistryFetcher(fixture_registry_config)


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
        ],
    )


@pytest.fixture
def fixture_registry_with_entity(
    fixture_registry: RegistryFetcher,
    sample_entity_create_resource: schemas.EntityCreate,
    fixture_db: Session,
):
    """Create a registry fetcher instance with an entity for testing."""
    fixture_registry.register_entity(sample_entity_create_resource, fixture_db)
    fixture_db.commit()
    yield fixture_registry
