from eunomia.instrument import Instrument
from eunomia.orchestra import Orchestra


class IdbacInstrument(Instrument):
    """
    An instrument that implements an ID-based access control (IDBAC) on input documents.
    IDBAC allows to specify a set of instruments that will be run only on those documents
    that are associated to different IDs than the one of the user.
    """

    def __init__(self, instruments: Instrument) -> None:
        self._orchestra = Orchestra(instruments=instruments)

    def run(self, text: str, **kwargs) -> str:
        user_id = kwargs.get("user_id")
        doc_id = kwargs.get("doc_id")

        if (user_id is not None) and (user_id == doc_id):
            return text
        return self._orchestra.run(text, **kwargs)
