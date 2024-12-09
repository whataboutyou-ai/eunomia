from eunomia.instrument import Instrument
from eunomia.orchestra import Orchestra


class RbacInstrument(Instrument):
    """
    An instrument that implements a role-based access control (RBAC) on input documents.
    RBAC allows to specify different instruments for each role, creating separate orchestras.
    """

    def __init__(self, role: str, instruments: Instrument) -> None:
        self._role = role
        self._orchestra = Orchestra(instruments=instruments)

    def run(self, text: str, **kwargs) -> str:
        if kwargs.get("role") == self._role:
            return self._orchestra.run(text, **kwargs)
        return text
