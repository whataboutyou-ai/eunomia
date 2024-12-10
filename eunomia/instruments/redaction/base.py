from abc import ABC, abstractmethod

from eunomia.instruments.identification.base import IdentificationResult


class BaseRedactor(ABC):
    """Base class for redaction modules."""

    @abstractmethod
    def redact(self, text: str, identifications: list[IdentificationResult]) -> str:
        """Redact entities from the text based on identifications."""
        ...
