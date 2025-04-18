from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseFetcherConfig(BaseModel):
    pass


class BaseFetcher(ABC):
    @abstractmethod
    def fetch_attributes(self, uri: str) -> dict: ...
