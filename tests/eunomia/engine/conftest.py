import pytest
from eunomia_core import enums, schemas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eunomia.engine.db import db
from eunomia.engine.engine import PolicyEngine


@pytest.fixture(scope="function")
def fixture_db():
    """Create an in-memory SQLite database for testing.
    - Each test function gets its own isolated database.
    - The database is created in memory at the start of each test.
    - The database is destroyed after each test completes.
    - No persistence between tests ensures test isolation.
    """
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
def fixture_engine(monkeypatch):
    """Create a PolicyEngine instance for testing with an in-memory database."""
    # Set up a test database URL
    monkeypatch.setattr(
        "eunomia.config.settings.ENGINE_SQL_DATABASE_URL", "sqlite:///:memory:"
    )

    # Initialize the engine
    engine = PolicyEngine()

    # Return the engine for testing
    yield engine


@pytest.fixture
def sample_policy():
    """Create a sample policy for testing."""
    return schemas.Policy(
        version="1.0",
        name="test-policy",
        description="Test policy",
        rules=[
            schemas.Rule(
                name="test-rule",
                effect=enums.PolicyEffect.ALLOW,
                principal_conditions=[
                    schemas.Condition(
                        path="attributes.role",
                        operator=enums.ConditionOperator.EQUALS,
                        value="admin",
                    )
                ],
                resource_conditions=[],
                actions=["access"],
            )
        ],
        default_effect=enums.PolicyEffect.DENY,
    )


@pytest.fixture
def sample_access_request():
    return schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "admin"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"name": "test-resource"},
        ),
        action="access",
    )
