from .factory import FetcherFactory
from .internal import InternalFetcher, InternalFetcherConfig, internal_router_factory

# Register the built-in fetchers
FetcherFactory.register_fetcher(
    "internal",
    InternalFetcher,
    InternalFetcherConfig,
    router_factory=internal_router_factory,
)


__all__ = ["FetcherFactory"]
