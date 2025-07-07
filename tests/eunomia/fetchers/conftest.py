import pytest
from unittest.mock import Mock
from eunomia_core import enums, schemas
from eunomia.fetchers.base import BaseFetcher, BaseFetcherConfig
from eunomia.fetchers.factory import FetcherFactory


class MockFetcherConfig(BaseFetcherConfig):
    test_param: str = "test_value"


class MockFetcher(BaseFetcher):
    def __init__(self, config: MockFetcherConfig):
        super().__init__(config)
        self.config = config

    async def fetch_attributes(self, uri: str) -> dict:
        return {"mock": "attributes", "uri": uri}


@pytest.fixture
def mock_fetcher_config():
    return MockFetcherConfig(test_param="test_value")


@pytest.fixture
def sample_entity_create():
    return schemas.EntityCreate(
        uri="test://entity/1",
        type=enums.EntityType.resource,
        attributes=[
            schemas.Attribute(key="name", value="Test Entity"),
            schemas.Attribute(key="role", value="admin"),
            schemas.Attribute(key="tags", value=["tag1", "tag2"]),
        ]
    )


@pytest.fixture
def sample_entity_update():
    return schemas.EntityUpdate(
        uri="test://entity/1",
        attributes=[
            schemas.Attribute(key="name", value="Updated Entity"),
            schemas.Attribute(key="department", value="engineering"),
        ]
    )


@pytest.fixture
def sample_entity_in_db():
    return schemas.EntityInDb(
        uri="test://entity/1",
        type=enums.EntityType.resource,
        attributes={"name": "Test Entity", "role": "admin"},
    )


@pytest.fixture
def clean_factory():
    """Clean the factory state before each test"""
    original_registry = FetcherFactory._registry.copy()
    original_instances = FetcherFactory._instances.copy()
    original_routers = FetcherFactory._routers.copy()
    
    # Clear the factory state
    FetcherFactory._registry.clear()
    FetcherFactory._instances.clear()
    FetcherFactory._routers.clear()
    
    yield
    
    # Restore original state
    FetcherFactory._registry = original_registry
    FetcherFactory._instances = original_instances
    FetcherFactory._routers = original_routers


@pytest.fixture
def router_factory():
    """Mock router factory"""
    from fastapi import APIRouter
    
    def mock_router_factory(fetcher):
        router = APIRouter()
        
        @router.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        return router
    
    return mock_router_factory