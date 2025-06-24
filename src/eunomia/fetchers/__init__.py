from .factory import FetcherFactory
from .internal import InternalFetcher, InternalFetcherConfig, internal_router_factory
from .passport import PassportFetcher, PassportFetcherConfig

# Register the built-in fetchers
FetcherFactory.register_fetcher(
    "internal",
    InternalFetcher,
    InternalFetcherConfig,
    router_factory=internal_router_factory,
)

FetcherFactory.register_fetcher(
    "passport",
    PassportFetcher,
    PassportFetcherConfig,
)


__all__ = ["FetcherFactory"]
