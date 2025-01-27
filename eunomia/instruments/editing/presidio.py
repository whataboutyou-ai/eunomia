from presidio_anonymizer import AnonymizerEngine, OperatorConfig, RecognizerResult

from eunomia.instruments.editing.base import BaseEditor
from eunomia.instruments.identification.base import IdentificationResult


class PresidioEditor(BaseEditor):
    """Presidio-based editing module."""

    def __init__(self, edit_mode: str) -> None:
        self._anonymizer = AnonymizerEngine()
        self._mode = edit_mode

    def edit(self, text: str, identifications: list[IdentificationResult]) -> str:
        return self._anonymizer.anonymize(
            text=text,
            analyzer_results=[
                RecognizerResult(**i.model_dump()) for i in identifications
            ],
            operators={"DEFAULT": OperatorConfig(self._mode, {})},
        ).text
