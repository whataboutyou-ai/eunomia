from eunomia_core import enums, schemas

from eunomia.engine.evaluator import (
    apply_operator,
    evaluate_condition,
    evaluate_conditions,
    evaluate_policy,
    evaluate_rule,
    get_attribute_value,
)


class DummyObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_get_attribute_value():
    obj = DummyObject(attr1=DummyObject(attr2="value"))
    assert get_attribute_value(obj, "attr1.attr2") == "value"
    assert get_attribute_value(obj, "attr1.nonexistent") is None

    dict_obj = {"attr1": {"attr2": "value"}}
    assert get_attribute_value(dict_obj, "attr1.attr2") == "value"
    assert get_attribute_value(dict_obj, "attr1.nonexistent") is None

    list_obj = [{"attr": "value"}]
    assert get_attribute_value(list_obj, "0.attr") == "value"
    assert get_attribute_value(list_obj, "1.attr") is None


def test_apply_operator():
    # String equality operators
    assert apply_operator(enums.ConditionOperator.EQUALS, "test", "test") is True
    assert apply_operator(enums.ConditionOperator.EQUALS, "test", "other") is False
    assert apply_operator(enums.ConditionOperator.NOT_EQUALS, "test", "other") is True
    assert apply_operator(enums.ConditionOperator.NOT_EQUALS, "test", "test") is False

    # String content operators
    assert apply_operator(enums.ConditionOperator.CONTAINS, "est", "test") is True
    assert apply_operator(enums.ConditionOperator.CONTAINS, "xyz", "test") is False
    assert apply_operator(enums.ConditionOperator.NOT_CONTAINS, "xyz", "test") is True
    assert apply_operator(enums.ConditionOperator.NOT_CONTAINS, "est", "test") is False

    # String position operators
    assert apply_operator(enums.ConditionOperator.STARTS_WITH, "te", "test") is True
    assert apply_operator(enums.ConditionOperator.STARTS_WITH, "st", "test") is False
    assert apply_operator(enums.ConditionOperator.ENDS_WITH, "st", "test") is True
    assert apply_operator(enums.ConditionOperator.ENDS_WITH, "te", "test") is False

    # Number equality operators
    assert apply_operator(enums.ConditionOperator.EQUALS, 1, 1) is True
    assert apply_operator(enums.ConditionOperator.EQUALS, 1, 2) is False
    assert apply_operator(enums.ConditionOperator.NOT_EQUALS, 1, 2) is True
    assert apply_operator(enums.ConditionOperator.NOT_EQUALS, 1, 1) is False

    # Number comparison operators
    assert apply_operator(enums.ConditionOperator.GREATER, 5, 3) is True
    assert apply_operator(enums.ConditionOperator.GREATER, 3, 5) is False
    assert apply_operator(enums.ConditionOperator.GREATER, 5, 5) is False
    assert apply_operator(enums.ConditionOperator.GREATER_OR_EQUAL, 5, 3) is True
    assert apply_operator(enums.ConditionOperator.GREATER_OR_EQUAL, 5, 5) is True
    assert apply_operator(enums.ConditionOperator.GREATER_OR_EQUAL, 3, 5) is False
    assert apply_operator(enums.ConditionOperator.LESS, 3, 5) is True
    assert apply_operator(enums.ConditionOperator.LESS, 5, 3) is False
    assert apply_operator(enums.ConditionOperator.LESS, 5, 5) is False
    assert apply_operator(enums.ConditionOperator.LESS_OR_EQUAL, 3, 5) is True
    assert apply_operator(enums.ConditionOperator.LESS_OR_EQUAL, 5, 5) is True
    assert apply_operator(enums.ConditionOperator.LESS_OR_EQUAL, 5, 3) is False

    # Float comparison operators
    assert apply_operator(enums.ConditionOperator.GREATER, 5.5, 3.2) is True
    assert apply_operator(enums.ConditionOperator.GREATER, 3.2, 5.5) is False
    assert apply_operator(enums.ConditionOperator.LESS_OR_EQUAL, 3.14, 3.14) is True

    # Mixed int/float comparison
    assert apply_operator(enums.ConditionOperator.GREATER, 5, 3.5) is True
    assert apply_operator(enums.ConditionOperator.LESS, 3.5, 5) is True

    # List membership operators
    assert (
        apply_operator(enums.ConditionOperator.IN, ["admin", "user"], "admin") is True
    )
    assert (
        apply_operator(enums.ConditionOperator.IN, ["admin", "user"], "guest") is False
    )
    assert (
        apply_operator(enums.ConditionOperator.NOT_IN, ["admin", "user"], "guest")
        is True
    )
    assert (
        apply_operator(enums.ConditionOperator.NOT_IN, ["admin", "user"], "admin")
        is False
    )

    # List with numbers
    assert apply_operator(enums.ConditionOperator.IN, [1, 2, 3], 2) is True
    assert apply_operator(enums.ConditionOperator.IN, [1, 2, 3], 4) is False
    assert apply_operator(enums.ConditionOperator.NOT_IN, [1, 2, 3], 4) is True
    assert apply_operator(enums.ConditionOperator.NOT_IN, [1, 2, 3], 2) is False

    # Empty list
    assert apply_operator(enums.ConditionOperator.IN, [], "anything") is False
    assert apply_operator(enums.ConditionOperator.NOT_IN, [], "anything") is True

    # None value handling
    assert apply_operator(enums.ConditionOperator.EQUALS, None, "test") is False
    assert apply_operator(enums.ConditionOperator.EQUALS, "test", None) is False
    assert apply_operator(enums.ConditionOperator.NOT_EQUALS, None, "test") is False
    assert apply_operator(enums.ConditionOperator.NOT_EQUALS, "test", None) is False

    # Invalid operator combinations should return False
    assert apply_operator(enums.ConditionOperator.CONTAINS, 123, "test") is False
    assert apply_operator(enums.ConditionOperator.STARTS_WITH, 123, "test") is False
    assert apply_operator(enums.ConditionOperator.GREATER, "abc", "def") is False
    assert apply_operator(enums.ConditionOperator.IN, "not_a_list", "test") is False


def test_evaluate_condition():
    condition = schemas.Condition(
        path="attributes.role", operator=enums.ConditionOperator.EQUALS, value="admin"
    )
    obj = DummyObject(attributes={"role": "admin"})
    assert evaluate_condition(condition, obj) is True

    obj = DummyObject(attributes={"role": "user"})
    assert evaluate_condition(condition, obj) is False


def test_evaluate_conditions():
    conditions = [
        schemas.Condition(
            path="attributes.role",
            operator=enums.ConditionOperator.EQUALS,
            value="admin",
        ),
        schemas.Condition(
            path="attributes.department",
            operator=enums.ConditionOperator.EQUALS,
            value="engineering",
        ),
    ]
    obj = DummyObject(attributes={"role": "admin", "department": "engineering"})
    assert evaluate_conditions(conditions, obj) is True

    obj = DummyObject(attributes={"role": "admin", "department": "marketing"})
    assert evaluate_conditions(conditions, obj) is False

    assert evaluate_conditions([], obj) is True


def test_evaluate_rule():
    rule = schemas.Rule(
        name="test-rule",
        effect=enums.PolicyEffect.ALLOW,
        principal_conditions=[
            schemas.Condition(
                path="attributes.role",
                operator=enums.ConditionOperator.EQUALS,
                value="admin",
            )
        ],
        resource_conditions=[
            schemas.Condition(
                path="attributes.type",
                operator=enums.ConditionOperator.EQUALS,
                value="document",
            )
        ],
        actions=["access"],
    )

    request = schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "admin"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"type": "document"},
        ),
        action="access",
    )
    assert evaluate_rule(rule, request) is True

    request = schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "user"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"type": "document"},
        ),
        action="access",
    )
    assert evaluate_rule(rule, request) is False

    request = schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "admin"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"type": "image"},
        ),
        action="access",
    )
    assert evaluate_rule(rule, request) is False

    request = schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "admin"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"type": "document"},
        ),
        action="delete",
    )
    assert evaluate_rule(rule, request) is False


def test_evaluate_policy():
    policy = schemas.Policy(
        version="1.0",
        name="test-policy",
        description="Test policy",
        rules=[
            schemas.Rule(
                name="test-rule",
                effect=enums.PolicyEffect.ALLOW,
                principal_conditions=[
                    schemas.Condition(
                        path="attributes.role",
                        operator=enums.ConditionOperator.EQUALS,
                        value="admin",
                    )
                ],
                resource_conditions=[],
                actions=["access"],
            )
        ],
        default_effect=enums.PolicyEffect.DENY,
    )

    request = schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "admin"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"name": "test-resource"},
        ),
        action="access",
    )
    result = evaluate_policy(policy, request)
    assert result.effect == enums.PolicyEffect.ALLOW
    assert result.matched_rule is not None
    assert result.policy_name == "test-policy"

    request = schemas.CheckRequest(
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
    result = evaluate_policy(policy, request)
    assert result.effect == enums.PolicyEffect.DENY
    assert result.matched_rule is None
    assert result.policy_name == "test-policy"
