from transformers import pipeline

from eunomia.instrument import Instrument
from eunomia.instruments.identification.base import IdentificationResult
from eunomia.instruments.redaction.presidio import PresidioRedactor


class FinancialsInstrument(Instrument):
    """
    An instrument that identifies financial entities in a text using a transformer-based NER model
    and redacts them using Presidio.

    Model information can be found at: https://huggingface.co/whataboutyou-ai/financial_bert.
    """

    def __init__(self, entities: list[str], redact_mode: str, language: str = "en"):
        self._redactor = PresidioRedactor(redact_mode=redact_mode)
        self._entities = entities
        self._ner_pipeline = pipeline(
            "token-classification", model="whataboutyou-ai/financial_bert"
        )

    def _merge_entities(self, entities: list[dict]) -> list[IdentificationResult]:
        merged_entities = []
        current_entity = None

        for entity in entities:
            prefix, entity_type = entity["entity"].split("-", 1)

            if (
                prefix == "I"
                and current_entity
                and current_entity.entity_type == entity_type
            ):
                # Continuation of the same entity
                current_entity.end = entity["end"]
                # Update score if desired, here we take min as a simplistic approach
                current_entity.score = min(current_entity.score, entity["score"].item())
            else:
                # Start of a new entity
                if current_entity:
                    merged_entities.append(current_entity)
                current_entity = IdentificationResult(
                    entity_type=entity_type,
                    start=entity["start"],
                    end=entity["end"],
                    score=entity["score"].item(),
                )

        if current_entity:
            merged_entities.append(current_entity)

        return merged_entities

    def run(self, text: str, **kwargs) -> str:
        # identification
        splitted_entities = self._ner_pipeline(text)
        merged_entities = self._merge_entities(splitted_entities)
        identifications = [
            entity for entity in merged_entities if entity.entity_type in self._entities
        ]

        # redaction
        return self._redactor.redact(text, identifications)
