from eunomia.instrument import Instrument
from eunomia.instruments.identification import TransformerIdentifier
from eunomia.instruments.redaction import PresidioRedactor


class FinancialsInstrument(Instrument):
    """
    An instrument that identifies financial entities in a text using a transformer-based NER model
    and redacts them using Presidio.

    Model information can be found at: https://huggingface.co/whataboutyou-ai/financial_bert.
    """

    _MODEL = "whataboutyou-ai/financial_bert"

    def __init__(self, entities: list[str], redact_mode: str):
        self._identifier = TransformerIdentifier(model=self._MODEL, entities=entities)
        self._redactor = PresidioRedactor(redact_mode=redact_mode)

    def run(self, text: str, **kwargs) -> str:
        identifications = self._identifier.identify(text)
        return self._redactor.redact(text, identifications)
