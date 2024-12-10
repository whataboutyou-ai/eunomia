from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class IdentificationResult(BaseModel):
    start: int
    end: int
    entity_type: str
    score: Optional[float]


class BaseIdentifier(ABC):
    """Base class for identification modules."""

    @abstractmethod
    def identify(self, text: str) -> list[IdentificationResult]:
        """Identify entities in a given text."""
        ...
