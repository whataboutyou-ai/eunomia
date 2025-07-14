from .factory import FetcherFactory
from .passport import PassportFetcher, PassportFetcherConfig, passport_router_factory
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
    router_factory=passport_router_factory,
)

__all__ = ["FetcherFactory"]
