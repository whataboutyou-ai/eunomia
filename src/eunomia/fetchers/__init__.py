from .factory import FetcherFactory
from .passport import PassportFetcher, PassportFetcherConfig
from .registry import RegistryFetcher, RegistryFetcherConfig, registry_router_factory

# Register the built-in fetchers
FetcherFactory.register_fetcher(
    "registry",
    RegistryFetcher,
    RegistryFetcherConfig,
    router_factory=registry_router_factory,
)

FetcherFactory.register_fetcher(
    "passport",
    PassportFetcher,
    PassportFetcherConfig,
)

__all__ = ["FetcherFactory"]
