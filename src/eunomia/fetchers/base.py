from abc import ABC, abstractmethod

from eunomia_core import schemas
from pydantic import BaseModel


class BaseFetcherConfig(BaseModel):
    id: str


class BaseFetcher(ABC):
    config: BaseFetcherConfig

    def __init__(self, config: BaseFetcherConfig):
        self.config = config

    @abstractmethod
    def register_entity(self, entity: schemas.EntityCreate) -> None: ...

    @abstractmethod
    def update_entity(self, entity: schemas.EntityUpdate, override: bool) -> None: ...

    @abstractmethod
    def delete_entity(self, uri: str) -> None: ...

    @abstractmethod
    def fetch_attributes(self, uri: str) -> dict: ...
