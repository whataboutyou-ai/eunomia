from eunomia.instruments.financials_instrument import FinancialsInstrument


def test_financials_instrument_initialization(
    financial_instrument: FinancialsInstrument,
) -> None:
    assert financial_instrument._entities == [
        "Advisors.GENERIC_CONSULTING_COMPANY",
        "Parties.BUYING_COMPANY",
    ]
    assert financial_instrument._redactor._mode == "replace"
    assert isinstance(
        financial_instrument._ner_pipeline, object
    )  # Verify pipeline exists


def test_financials_instrument_run(
    financial_instrument: FinancialsInstrument, financial_sample_text: str
) -> None:
    result = financial_instrument.run(financial_sample_text)
    # Original company names should be redacted
    assert "Smithson Legal Advisors" not in result
    assert "Bellcom Industries" not in result
    # Other text should remain
    assert "provided counsel to" in result
    assert "in their acquisition" in result
