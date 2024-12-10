from presidio_anonymizer import AnonymizerEngine, OperatorConfig, RecognizerResult

from eunomia.instruments.identification.base import IdentificationResult
from eunomia.instruments.redaction.base import BaseRedactor


class PresidioRedactor(BaseRedactor):
    """Presidio-based redaction module."""

    def __init__(self, redact_mode: str) -> None:
        self._anonymizer = AnonymizerEngine()
        self._mode = redact_mode

    def redact(self, text: str, identifications: list[IdentificationResult]) -> str:
        return self._anonymizer.anonymize(
            text=text,
            analyzer_results=[
                RecognizerResult(**i.model_dump()) for i in identifications
            ],
            operators={"DEFAULT": OperatorConfig(self._mode, {})},
        ).text
