from eunomia.instrument import Instrument, InstrumentConfig
from eunomia.instruments.editing import PresidioEditor
from eunomia.instruments.identification import TransformerIdentifier
from eunomia.utils.enums import RetrievalStage


class FinancialsInstrument(Instrument):
    """
    An instrument that identifies financial entities in a text using a transformer-based NER model
    and edits them using Presidio.

    Model information can be found at: https://huggingface.co/whataboutyou-ai/financial_bert.
    """

    _MODEL = "whataboutyou-ai/financial_bert"

    def __init__(self, entities: list[str], edit_mode: str):
        self.config = InstrumentConfig(
            id="financials",
            retrieval_stage=RetrievalStage.POST,
        )
        self._identifier = TransformerIdentifier(model=self._MODEL, entities=entities)
        self._editor = PresidioEditor(edit_mode=edit_mode)

    def run(self, text: str, **kwargs) -> str:
        identifications = self._identifier.identify(text)
        return self._editor.edit(text, identifications)
