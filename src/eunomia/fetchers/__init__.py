from .factory import FetcherFactory
from .registry import RegistryFetcher, RegistryFetcherConfig, registry_router_factory

# Register the built-in fetchers
FetcherFactory.register_fetcher(
    "registry",
    RegistryFetcher,
    RegistryFetcherConfig,
    router_factory=registry_router_factory,
)


__all__ = ["FetcherFactory"]
