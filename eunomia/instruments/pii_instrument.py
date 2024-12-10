from eunomia.instrument import Instrument
from eunomia.instruments.identification import PresidioIdentifier
from eunomia.instruments.redaction import PresidioRedactor


class PiiInstrument(Instrument):
    """
    An instrument that redacts PII entities in a text using Presidio.
    """

    def __init__(self, entities: list[str], redact_mode: str, language: str = "en"):
        self._identifier = PresidioIdentifier(entities, language)
        self._redactor = PresidioRedactor(redact_mode)

    def run(self, text: str, **kwargs) -> str:
        identifications = self._identifier.identify(text)
        return self._redactor.redact(text, identifications)
