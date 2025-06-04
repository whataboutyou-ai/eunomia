from eunomia_core import enums, schemas

from eunomia.engine import PolicyEngine


def test_add_policy(fixture_engine: PolicyEngine, sample_policy: schemas.Policy):
    fixture_engine.add_policy(sample_policy)
    assert len(fixture_engine.policies) == 1
    assert fixture_engine.policies[0].name == sample_policy.name


def test_remove_policy(fixture_engine: PolicyEngine, sample_policy: schemas.Policy):
    fixture_engine.add_policy(sample_policy)
    assert fixture_engine.remove_policy("test-policy") is True
    assert len(fixture_engine.policies) == 0
    assert fixture_engine.remove_policy("non-existent") is False


def test_get_policy(fixture_engine: PolicyEngine, sample_policy: schemas.Policy):
    fixture_engine.add_policy(sample_policy)
    retrieved = fixture_engine.get_policy("test-policy")
    assert retrieved.name == sample_policy.name
    assert fixture_engine.get_policy("non-existent") is None


def test_evaluate_all_with_no_policies(
    fixture_engine: PolicyEngine, sample_access_request: schemas.CheckRequest
):
    result = fixture_engine.evaluate_all(sample_access_request)
    assert result.allowed is False
    assert "default" in result.reason


def test_evaluate_all_with_matching_policy(
    fixture_engine: PolicyEngine,
    sample_policy: schemas.Policy,
    sample_access_request: schemas.CheckRequest,
):
    fixture_engine.add_policy(sample_policy)
    result = fixture_engine.evaluate_all(sample_access_request)
    assert result.allowed is True
    assert "test-policy" in result.reason


def test_evaluate_all_with_non_matching_policy(
    fixture_engine: PolicyEngine, sample_policy: schemas.Policy
):
    non_matching_request = schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "user"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"name": "test-resource"},
        ),
        action="access",
    )
    fixture_engine.add_policy(sample_policy)
    result = fixture_engine.evaluate_all(non_matching_request)
    assert result.allowed is False
