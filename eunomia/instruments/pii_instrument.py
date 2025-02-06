from eunomia.instrument import Instrument, InstrumentConfig
from eunomia.instruments.editing import PresidioEditor
from eunomia.instruments.identification import PresidioIdentifier
from eunomia.utils.enums import RetrievalStage


class PiiInstrument(Instrument):
    """
    An instrument that edits PII entities in a text using Presidio.
    """

    def __init__(self, entities: list[str], edit_mode: str, language: str = "en"):
        self.config = InstrumentConfig(
            id="pii",
            retrieval_stage=RetrievalStage.POST,
        )
        self._identifier = PresidioIdentifier(entities, language)
        self._editor = PresidioEditor(edit_mode)

    def run(self, text: str, **kwargs) -> str:
        identifications = self._identifier.identify(text)
        return self._editor.edit(text, identifications)
