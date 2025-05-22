from abc import ABC, abstractmethod
from typing import Optional

from eunomia_core import enums
from pydantic import BaseModel


class BaseFetcherConfig(BaseModel):
    entity_type: Optional[enums.EntityType] = None


class BaseFetcher(ABC):
    config: BaseFetcherConfig

    def __init__(self, config: BaseFetcherConfig):
        self.config = config

    @abstractmethod
    async def fetch_attributes(self, uri: str) -> dict: ...
