from abc import ABC, abstractmethod

from eunomia.instruments.identification.base import IdentificationResult


class BaseEditor(ABC):
    """Base class for editing modules."""

    @abstractmethod
    def edit(self, text: str, identifications: list[IdentificationResult]) -> str:
        """Edit entities from the text based on identifications."""
        ...
