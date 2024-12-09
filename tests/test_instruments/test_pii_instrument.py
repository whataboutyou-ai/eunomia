from eunomia.instruments.pii_instrument import PiiInstrument


def test_pii_instrument_initialization(pii_instrument: PiiInstrument) -> None:
    assert pii_instrument._entities == ["EMAIL_ADDRESS", "PERSON"]
    assert pii_instrument._redact_mode == "replace"
    assert pii_instrument._language == "en"


def test_pii_instrument_run(pii_instrument: PiiInstrument, sample_text: str) -> None:
    result = pii_instrument.run(sample_text)
    assert "john.doe@example.com" not in result
    assert "John Doe" not in result
    assert "Hello" in result
