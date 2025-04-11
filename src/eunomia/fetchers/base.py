from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseFetcherConfig(BaseModel):
    id: str


class BaseFetcher(ABC):
    config: BaseFetcherConfig

    def __init__(self, config: BaseFetcherConfig):
        self.config = config

    @abstractmethod
    def fetch_attributes(self, uri: str) -> dict: ...
