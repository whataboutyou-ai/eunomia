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

    def post_init(self) -> None:
        """
        Optional method that is called after all fetchers are initialized.
        It can be used for initialization that depends on other fetchers.
        """
        pass

    @abstractmethod
    async def fetch_attributes(self, uri: str) -> dict: ...
