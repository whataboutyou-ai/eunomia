from transformers import pipeline

from eunomia.instruments.identification.base import BaseIdentifier, IdentificationResult


class TransformerIdentifier(BaseIdentifier):
    """Transformer-based NER identification module."""

    def __init__(self, model: str, entities: list[str]):
        self._pipeline = pipeline("token-classification", model=model)
        self._entities = entities

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

    def identify(self, text: str) -> list[IdentificationResult]:
        splitted_entities = self._pipeline(text)
        merged_entities = self._merge_entities(splitted_entities)
        return [
            entity for entity in merged_entities if entity.entity_type in self._entities
        ]
