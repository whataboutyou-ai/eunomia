import pytest
from eunomia_core.schemas import (
    AccessRequest,
    EntityType,
    PrincipalAccess,
    ResourceAccess,
)

from eunomia.engine import PolicyEngine, schemas


@pytest.fixture
def engine() -> PolicyEngine:
    return PolicyEngine()


@pytest.fixture
def sample_policy() -> schemas.Policy:
    return schemas.Policy(
        name="test-policy",
        description="Test policy",
        rules=[
            schemas.Rule(
                description="Test rule",
                effect=schemas.PolicyEffect.ALLOW,
                principal_conditions=[
                    schemas.Condition(
                        path="attributes.role",
                        operator=schemas.ConditionOperator.EQUALS,
                        value="admin",
                    )
                ],
                resource_conditions=[],
                actions=["access"],
            )
        ],
        default_effect=schemas.PolicyEffect.DENY,
    )


@pytest.fixture
def access_request() -> AccessRequest:
    return AccessRequest(
        principal=PrincipalAccess(
            type=EntityType.principal,
            attributes={"role": "admin"},
        ),
        resource=ResourceAccess(
            type=EntityType.resource,
            attributes={"name": "test-resource"},
        ),
        action="access",
    )


def test_add_policy(engine: PolicyEngine, sample_policy: schemas.Policy):
    engine.add_policy(sample_policy)
    assert len(engine.policies) == 1
    assert engine.policies[0] == sample_policy


def test_remove_policy(engine: PolicyEngine, sample_policy: schemas.Policy):
    engine.add_policy(sample_policy)
    assert engine.remove_policy("test-policy") is True
    assert len(engine.policies) == 0
    assert engine.remove_policy("non-existent") is False


def test_get_policy(engine: PolicyEngine, sample_policy: schemas.Policy):
    engine.add_policy(sample_policy)
    retrieved = engine.get_policy("test-policy")
    assert retrieved == sample_policy
    assert engine.get_policy("non-existent") is None


def test_evaluate_all_with_no_policies(
    engine: PolicyEngine, access_request: AccessRequest
):
    result = engine.evaluate_all(access_request)
    assert result.effect == schemas.PolicyEffect.DENY
    assert result.matched_rule is None
    assert result.policy_name == "default"


def test_evaluate_all_with_matching_policy(
    engine: PolicyEngine, sample_policy: schemas.Policy, access_request: AccessRequest
):
    engine.add_policy(sample_policy)
    result = engine.evaluate_all(access_request)
    assert result.effect == schemas.PolicyEffect.ALLOW
    assert result.matched_rule is not None
    assert result.policy_name == "test-policy"


def test_evaluate_all_with_non_matching_policy(
    engine: PolicyEngine, sample_policy: schemas.Policy
):
    non_matching_request = AccessRequest(
        principal=PrincipalAccess(
            type=EntityType.principal,
            attributes={"role": "user"},
        ),
        resource=ResourceAccess(
            type=EntityType.resource,
            attributes={"name": "test-resource"},
        ),
        action="access",
    )
    engine.add_policy(sample_policy)
    result = engine.evaluate_all(non_matching_request)
    assert result.effect == schemas.PolicyEffect.DENY
    assert result.matched_rule is None
    assert result.policy_name == "test-policy"
