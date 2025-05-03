from eunomia_core import enums

from eunomia.engine import utils


def test_create_attribute_condition():
    condition = utils.create_attribute_condition("role", "admin")
    assert condition.path == "attributes.role"
    assert condition.operator == enums.ConditionOperator.EQUALS
    assert condition.value == "admin"

    condition = utils.create_attribute_condition(
        "role", "admin", operator=enums.ConditionOperator.CONTAINS
    )
    assert condition.operator == enums.ConditionOperator.CONTAINS


def test_create_simple_policy():
    policy = utils.create_simple_policy(
        name="test-policy",
        description="Test policy",
        principal_attributes={"role": "admin"},
        resource_attributes={"type": "document"},
        effect=enums.PolicyEffect.ALLOW,
        default_effect=enums.PolicyEffect.DENY,
    )

    assert policy.name == "test-policy"
    assert policy.description == "Test policy"
    assert policy.default_effect == enums.PolicyEffect.DENY
    assert len(policy.rules) == 1

    rule = policy.rules[0]
    assert rule.effect == enums.PolicyEffect.ALLOW
    assert rule.actions == ["access"]
    assert len(rule.principal_conditions) == 1
    assert len(rule.resource_conditions) == 1

    principal_condition = rule.principal_conditions[0]
    assert principal_condition.path == "attributes.role"
    assert principal_condition.operator == enums.ConditionOperator.EQUALS
    assert principal_condition.value == "admin"

    resource_condition = rule.resource_conditions[0]
    assert resource_condition.path == "attributes.type"
    assert resource_condition.operator == enums.ConditionOperator.EQUALS
    assert resource_condition.value == "document"


def test_create_simple_policy_with_minimal_params():
    policy = utils.create_simple_policy(name="test-policy")

    assert policy.name == "test-policy"
    assert policy.description is None
    assert policy.default_effect == enums.PolicyEffect.DENY
    assert len(policy.rules) == 1

    rule = policy.rules[0]
    assert rule.effect == enums.PolicyEffect.ALLOW
    assert rule.actions == ["access"]
    assert len(rule.principal_conditions) == 0
    assert len(rule.resource_conditions) == 0
