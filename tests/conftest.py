import pytest

from eunomia.instruments import PiiInstrument, RbacInstrument
from eunomia.orchestra import Orchestra


@pytest.fixture
def sample_text() -> str:
    return "Hello, my name is John Doe and my email is john.doe@example.com."


@pytest.fixture
def pii_config() -> dict:
    return {"entities": ["EMAIL_ADDRESS", "PERSON"], "redact_mode": "replace"}


@pytest.fixture
def pii_instrument(pii_config: dict) -> PiiInstrument:
    return PiiInstrument(**pii_config)


@pytest.fixture
def role() -> str:
    return "specialist"


@pytest.fixture
def rbac_config(role: str) -> dict:
    return {
        "role": role,
        "instruments": [
            PiiInstrument(entities=["EMAIL_ADDRESS"], redact_mode="replace")
        ],
    }


@pytest.fixture
def rbac_instrument(rbac_config: dict) -> RbacInstrument:
    return RbacInstrument(**rbac_config)


@pytest.fixture
def orchestra() -> Orchestra:
    return Orchestra()
