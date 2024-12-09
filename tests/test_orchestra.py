from eunomia.instruments.pii_instrument import PiiInstrument
from eunomia.orchestra import Orchestra


def test_orchestra_initialization(orchestra: Orchestra) -> None:
    assert len(orchestra._instruments) == 0


def test_orchestra_add_instrument(
    orchestra: Orchestra, pii_instrument: PiiInstrument
) -> None:
    orchestra.add_instrument(pii_instrument)
    assert len(orchestra._instruments) == 1


def test_orchestra_run(
    orchestra: Orchestra, pii_instrument: PiiInstrument, sample_text: str
) -> None:
    orchestra.add_instrument(pii_instrument)
    result = orchestra.run(sample_text)
    assert "john.doe@example.com" not in result
    assert "John Doe" not in result
