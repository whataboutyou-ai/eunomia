import pytest

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


class TestFetcherFactory:
    """Test the FetcherFactory class functionality"""

    def test_register_fetcher_basic(self, clean_factory):
        """Test basic fetcher registration"""
        FetcherFactory.register_fetcher("test_fetcher", MockFetcher, MockFetcherConfig)

        assert "test_fetcher" in FetcherFactory._registry
        registry_entry = FetcherFactory._registry["test_fetcher"]
        assert registry_entry.fetcher_cls is MockFetcher
        assert registry_entry.config_cls is MockFetcherConfig
        assert registry_entry.router_factory is None

    def test_register_fetcher_with_router(self, clean_factory, router_factory):
        """Test fetcher registration with router factory"""
        FetcherFactory.register_fetcher(
            "test_fetcher", MockFetcher, MockFetcherConfig, router_factory
        )

        registry_entry = FetcherFactory._registry["test_fetcher"]
        assert registry_entry.router_factory == router_factory

    def test_create_fetcher_success(self, clean_factory, mock_fetcher_config):
        """Test successful fetcher creation"""
        FetcherFactory.register_fetcher("test_fetcher", MockFetcher, MockFetcherConfig)

        fetcher = FetcherFactory.create_fetcher("test_fetcher", mock_fetcher_config)

        assert isinstance(fetcher, MockFetcher)
        assert fetcher.config.test_param == "test_value"

    def test_create_fetcher_not_registered(self, clean_factory, mock_fetcher_config):
        """Test fetcher creation for unregistered fetcher"""
        with pytest.raises(ValueError, match="Fetcher not registered: unknown_fetcher"):
            FetcherFactory.create_fetcher("unknown_fetcher", mock_fetcher_config)

    def test_create_fetcher_invalid_config(self, clean_factory):
        """Test fetcher creation with invalid config"""
        FetcherFactory.register_fetcher("test_fetcher", MockFetcher, MockFetcherConfig)

        invalid_config = BaseFetcherConfig()
        with pytest.raises(ValueError):
            FetcherFactory.create_fetcher("test_fetcher", invalid_config)

    def test_initialize_fetchers_success(self, clean_factory, mock_fetcher_config):
        """Test successful fetcher initialization"""
        FetcherFactory.register_fetcher("test_fetcher", MockFetcher, MockFetcherConfig)

        configs = {"test_fetcher": mock_fetcher_config}
        FetcherFactory.initialize_fetchers(configs)

        assert "test_fetcher" in FetcherFactory._instances
        assert isinstance(FetcherFactory._instances["test_fetcher"], MockFetcher)

    def test_initialize_fetchers_with_router(
        self, clean_factory, mock_fetcher_config, router_factory
    ):
        """Test fetcher initialization with router factory"""
        FetcherFactory.register_fetcher(
            "test_fetcher", MockFetcher, MockFetcherConfig, router_factory
        )

        configs = {"test_fetcher": mock_fetcher_config}
        FetcherFactory.initialize_fetchers(configs)

        assert "test_fetcher" in FetcherFactory._instances
        assert "test_fetcher" in FetcherFactory._routers
        router = FetcherFactory._routers["test_fetcher"]
        assert router is not None

    def test_initialize_multiple_fetchers(self, clean_factory):
        """Test initializing multiple fetchers"""
        FetcherFactory.register_fetcher("fetcher1", MockFetcher, MockFetcherConfig)
        FetcherFactory.register_fetcher("fetcher2", MockFetcher, MockFetcherConfig)

        configs: dict[str, BaseFetcherConfig] = {
            "fetcher1": MockFetcherConfig(test_param="value1"),
            "fetcher2": MockFetcherConfig(test_param="value2"),
        }
        FetcherFactory.initialize_fetchers(configs)

        assert len(FetcherFactory._instances) == 2
        assert "fetcher1" in FetcherFactory._instances
        assert "fetcher2" in FetcherFactory._instances
        assert FetcherFactory._instances["fetcher1"].config.test_param == "value1"
        assert FetcherFactory._instances["fetcher2"].config.test_param == "value2"

    def test_get_fetcher_success(self, clean_factory, mock_fetcher_config):
        """Test successful fetcher retrieval"""
        FetcherFactory.register_fetcher("test_fetcher", MockFetcher, MockFetcherConfig)
        FetcherFactory.initialize_fetchers({"test_fetcher": mock_fetcher_config})

        fetcher = FetcherFactory.get_fetcher("test_fetcher")
        assert isinstance(fetcher, MockFetcher)

    def test_get_fetcher_not_initialized(self, clean_factory):
        """Test fetcher retrieval for uninitialized fetcher"""
        with pytest.raises(
            ValueError, match="Fetcher not initialized: unknown_fetcher"
        ):
            FetcherFactory.get_fetcher("unknown_fetcher")

    def test_get_all_fetchers(self, clean_factory):
        """Test retrieving all fetchers"""
        FetcherFactory.register_fetcher("fetcher1", MockFetcher, MockFetcherConfig)
        FetcherFactory.register_fetcher("fetcher2", MockFetcher, MockFetcherConfig)

        configs: dict[str, BaseFetcherConfig] = {
            "fetcher1": MockFetcherConfig(test_param="value1"),
            "fetcher2": MockFetcherConfig(test_param="value2"),
        }
        FetcherFactory.initialize_fetchers(configs)

        all_fetchers = FetcherFactory.get_all_fetchers()
        assert len(all_fetchers) == 2
        assert "fetcher1" in all_fetchers
        assert "fetcher2" in all_fetchers

    def test_get_router_success(
        self, clean_factory, mock_fetcher_config, router_factory
    ):
        """Test successful router retrieval"""
        FetcherFactory.register_fetcher(
            "test_fetcher", MockFetcher, MockFetcherConfig, router_factory
        )
        FetcherFactory.initialize_fetchers({"test_fetcher": mock_fetcher_config})

        router = FetcherFactory.get_router("test_fetcher")
        assert router is not None

    def test_get_router_not_available(self, clean_factory, mock_fetcher_config):
        """Test router retrieval for fetcher without router"""
        FetcherFactory.register_fetcher("test_fetcher", MockFetcher, MockFetcherConfig)
        FetcherFactory.initialize_fetchers({"test_fetcher": mock_fetcher_config})

        with pytest.raises(
            ValueError, match="Router not available for fetcher: test_fetcher"
        ):
            FetcherFactory.get_router("test_fetcher")

    def test_get_all_routers(self, clean_factory, router_factory):
        """Test retrieving all routers"""
        FetcherFactory.register_fetcher(
            "fetcher1", MockFetcher, MockFetcherConfig, router_factory
        )
        FetcherFactory.register_fetcher(
            "fetcher2", MockFetcher, MockFetcherConfig, router_factory
        )

        configs: dict[str, BaseFetcherConfig] = {
            "fetcher1": MockFetcherConfig(test_param="value1"),
            "fetcher2": MockFetcherConfig(test_param="value2"),
        }
        FetcherFactory.initialize_fetchers(configs)

        all_routers = FetcherFactory.get_all_routers()
        assert len(all_routers) == 2
        assert "fetcher1" in all_routers
        assert "fetcher2" in all_routers

    def test_empty_factory_state(self, clean_factory):
        """Test factory behavior with empty state"""
        assert len(FetcherFactory._registry) == 0
        assert len(FetcherFactory._instances) == 0
        assert len(FetcherFactory._routers) == 0

        with pytest.raises(ValueError):
            FetcherFactory.get_fetcher("any_fetcher")

        with pytest.raises(ValueError):
            FetcherFactory.get_router("any_fetcher")

        assert FetcherFactory.get_all_fetchers() == {}
        assert FetcherFactory.get_all_routers() == {}

    def test_factory_isolation(self, clean_factory):
        """Test that factory operations are isolated"""
        # Register in first "session"
        FetcherFactory.register_fetcher("test_fetcher", MockFetcher, MockFetcherConfig)

        # Clear and verify isolation
        FetcherFactory._registry.clear()
        assert len(FetcherFactory._registry) == 0

        # Register different fetcher
        FetcherFactory.register_fetcher("other_fetcher", MockFetcher, MockFetcherConfig)

        assert "other_fetcher" in FetcherFactory._registry
        assert "test_fetcher" not in FetcherFactory._registry
