import logging
from typing import Dict, Type

from pydantic import BaseModel

from eunomia.fetchers.base import BaseFetcher, BaseFetcherConfig
from eunomia.fetchers.internal import (
    InternalFetcher,
    InternalFetcherConfig,
)


class FetcherRegistryEntry(BaseModel):
    fetcher_cls: Type[BaseFetcher]
    config_cls: Type[BaseFetcherConfig]


class FetcherFactory:
    """
    Factory for creating and managing fetcher instances.

    This factory allows registering fetchers and creating
    instances based on configuration.
    """

    _registry: Dict[str, FetcherRegistryEntry] = {}
    _instances: Dict[str, BaseFetcher] = {}

    @classmethod
    def register_fetcher(
        cls,
        fetcher_id: str,
        fetcher_cls: Type[BaseFetcher],
        config_cls: Type[BaseFetcherConfig],
    ) -> None:
        cls._registry[fetcher_id] = FetcherRegistryEntry(
            fetcher_cls=fetcher_cls, config_cls=config_cls
        )
        logging.info(f"Registered fetcher: {fetcher_id}")

    @classmethod
    def create_fetcher(cls, fetcher_id: str, config: BaseFetcherConfig) -> BaseFetcher:
        if fetcher_id not in cls._registry:
            raise ValueError(f"Fetcher not registered: {fetcher_id}")

        registry_entry = cls._registry[fetcher_id]
        fetcher_config = registry_entry.config_cls.model_validate(config)
        return registry_entry.fetcher_cls(fetcher_config)

    @classmethod
    def initialize_fetchers(
        cls, fetcher_configs: dict[str, BaseFetcherConfig]
    ) -> Dict[str, BaseFetcher]:
        instances = {}

        for fetcher_id, fetcher_config in fetcher_configs.items():
            fetcher = cls.create_fetcher(fetcher_id=fetcher_id, config=fetcher_config)
            instances[fetcher_id] = fetcher
            logging.info(f"Initialized fetcher: {fetcher_id}")

        cls._instances = instances
        return instances

    @classmethod
    def get_fetcher(cls, fetcher_id: str) -> BaseFetcher:
        if fetcher_id not in cls._instances:
            raise ValueError(f"Fetcher not initialized: {fetcher_id}")
        return cls._instances[fetcher_id]


# Built-in fetchers
FetcherFactory.register_fetcher("internal", InternalFetcher, InternalFetcherConfig)
