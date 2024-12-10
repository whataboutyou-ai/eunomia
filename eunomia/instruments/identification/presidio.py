from presidio_analyzer import AnalyzerEngine

from eunomia.instruments.identification.base import BaseIdentifier, IdentificationResult


class PresidioIdentifier(BaseIdentifier):
    """Presidio-based identification module."""

    def __init__(self, entities: list[str], language: str):
        self._analyzer = AnalyzerEngine()
        self._entities = entities
        self._language = language

    def identify(self, text: str) -> list[IdentificationResult]:
        results = self._analyzer.analyze(
            text, entities=self._entities, language=self._language
        )
        return [
            IdentificationResult(
                entity_type=r.entity_type, start=r.start, end=r.end, score=r.score
            )
            for r in results
        ]
