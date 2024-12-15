from eunomia.instruments.pii_instrument import PiiInstrument


def test_pii_instrument_initialization(pii_instrument: PiiInstrument) -> None:
    assert pii_instrument._identifier._entities == ["EMAIL_ADDRESS", "PERSON"]
    assert pii_instrument._editor._mode == "replace"
    assert pii_instrument._identifier._language == "en"


def test_pii_instrument_run(
    pii_instrument: PiiInstrument, pii_sample_text: str
) -> None:
    result = pii_instrument.run(pii_sample_text)
    assert "john.doe@example.com" not in result
    assert "John Doe" not in result
    assert "Hello" in result
