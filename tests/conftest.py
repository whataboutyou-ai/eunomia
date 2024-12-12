import pytest

from eunomia.instruments import *
from eunomia.orchestra import Orchestra


@pytest.fixture
def orchestra() -> Orchestra:
    return Orchestra()


@pytest.fixture
def pii_sample_text() -> str:
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
def idbac_instrument(pii_instrument: PiiInstrument) -> IdbacInstrument:
    return IdbacInstrument(instruments=[pii_instrument])


@pytest.fixture
def financial_config() -> dict:
    return {
        "entities": ["Advisors.GENERIC_CONSULTING_COMPANY", "Parties.BUYING_COMPANY"],
        "redact_mode": "replace",
    }


@pytest.fixture
def financial_instrument(financial_config: dict) -> FinancialsInstrument:
    return FinancialsInstrument(**financial_config)


@pytest.fixture
def financial_sample_text() -> str:
    return "Smithson Legal Advisors provided counsel to Bellcom Industries, the buying company, in their acquisition."
