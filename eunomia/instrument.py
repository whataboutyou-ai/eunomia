from abc import ABC, abstractmethod
from dataclasses import dataclass

from eunomia.utils.enums import RetrievalStage


@dataclass
class InstrumentConfig:
    """Instrument configuration."""

    id: str
    retrieval_stage: RetrievalStage


class Instrument(ABC):
    """Base class for all instruments."""

    config: InstrumentConfig

    @abstractmethod
    def run(self, text: str, **kwargs) -> str:
        """Run the instrument on an input text."""
        pass
