import pytest

from eunomia.fetchers.factory import FetcherFactory


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
