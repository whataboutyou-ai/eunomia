from eunomia.instruments.rbac_instrument import RbacInstrument


def test_rbac_instrument_initialization(rbac_instrument: RbacInstrument) -> None:
    assert rbac_instrument._role == "specialist"
    assert len(rbac_instrument._orchestra._instruments) == 1


def test_rbac_instrument_run(
    rbac_instrument: RbacInstrument, sample_text: str, role: str
) -> None:
    result = rbac_instrument.run(sample_text, role=role)
    assert "john.doe@example.com" not in result
    assert "John Doe" in result
