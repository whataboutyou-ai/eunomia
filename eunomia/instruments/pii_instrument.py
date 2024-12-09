from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, OperatorConfig

from eunomia.instrument import Instrument


class PiiInstrument(Instrument):
    """
    An instrument that redacts PII entities in a text using Presidio.
    """

    def __init__(self, entities: list[str], redact_mode: str, language: str = "en"):
        self._analyzer = AnalyzerEngine()
        self._anonymizer = AnonymizerEngine()
        self._entities = entities
        self._redact_mode = redact_mode
        self._language = language

    def run(self, text: str, **kwargs) -> str:
        # Analyze the text to find PII entities
        analyzer_results = self._analyzer.analyze(
            text=text, entities=self._entities, language=self._language
        )

        # Anonymize the identified entities
        anonymized_text = self._anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={"DEFAULT": OperatorConfig(self._redact_mode, {})},
        )

        return anonymized_text.text
