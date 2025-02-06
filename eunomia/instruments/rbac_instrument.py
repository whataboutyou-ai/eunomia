from eunomia.instrument import Instrument, InstrumentConfig
from eunomia.orchestra import Orchestra
from eunomia.utils.enums import RetrievalStage


class RbacInstrument(Instrument):
    """
    An instrument that implements a role-based access control (RBAC) on input documents.
    RBAC allows to specify different instruments for each role, creating separate orchestras.
    """

    def __init__(self, role: str, instruments: Instrument) -> None:
        self.config = InstrumentConfig(
            id="rbac",
            retrieval_stage=RetrievalStage.POST,
        )
        self._role = role
        self._orchestra = Orchestra(instruments=instruments)

    def run(self, text: str, **kwargs) -> str:
        if kwargs.get("role") == self._role:
            return self._orchestra.run(text, **kwargs)
        return text
