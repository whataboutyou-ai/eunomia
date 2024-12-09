from abc import ABC, abstractmethod


class Instrument(ABC):
    @abstractmethod
    def run(self, text: str, **kwargs) -> str:
        """Run the instrument on an input text."""
        pass
