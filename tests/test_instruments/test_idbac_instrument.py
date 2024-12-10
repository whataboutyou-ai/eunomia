from eunomia.instruments.idbac_instrument import IdbacInstrument


def test_idbac_instrument_initialization(idbac_instrument: IdbacInstrument) -> None:
    assert len(idbac_instrument._orchestra._instruments) == 1


def test_idbac_instrument_run_different_ids(
    idbac_instrument: IdbacInstrument, sample_text: str
) -> None:
    # When user_id and doc_id are different, the nested instruments should run
    result = idbac_instrument.run(sample_text, user_id="user1", doc_id="user2")
    assert "john.doe@example.com" not in result


def test_idbac_instrument_run_same_ids(
    idbac_instrument: IdbacInstrument, sample_text: str
) -> None:
    # When user_id and doc_id are the same, the text should pass through unchanged
    result = idbac_instrument.run(sample_text, user_id="user1", doc_id="user1")
    assert result == sample_text
    assert "john.doe@example.com" in result


def test_idbac_instrument_run_missing_ids(
    idbac_instrument: IdbacInstrument, sample_text: str
) -> None:
    # When ids are missing, the nested instruments should run
    result = idbac_instrument.run(sample_text)
    assert "john.doe@example.com" not in result
