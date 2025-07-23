import pytest
from eunomia_core.enums.policy import ConditionOperator, PolicyEffect
from eunomia_core.schemas.policy import (
    Condition,
    Policy,
    PolicyEvaluationResult,
    Rule,
)
from pydantic import ValidationError


@pytest.fixture
def valid_condition():
    return {
        "path": "attributes.role",
        "operator": ConditionOperator.EQUALS,
        "value": "admin",
    }


@pytest.fixture
def valid_condition_with_json_value():
    return {
        "path": "attributes.permissions",
        "operator": ConditionOperator.IN,
        "value": '["read", "write"]',
    }


@pytest.fixture
def valid_rule():
    return {
        "name": "Allow Admin Access",
        "effect": PolicyEffect.ALLOW,
        "actions": ["read", "write"],
    }


@pytest.fixture
def valid_rule_with_conditions():
    return {
        "name": "Complex Rule",
        "description": "A rule with conditions",
        "effect": PolicyEffect.ALLOW,
        "principal_conditions": [
            {
                "path": "attributes.role",
                "operator": ConditionOperator.EQUALS,
                "value": "admin",
            }
        ],
        "resource_conditions": [
            {
                "path": "attributes.category",
                "operator": ConditionOperator.IN,
                "value": ["public", "shared"],
            }
        ],
        "actions": ["read", "write", "delete"],
    }


@pytest.fixture
def valid_policy():
    return {
        "name": "Test Policy",
        "description": "A test policy",
        "rules": [
            {
                "name": "allow-admin",
                "effect": PolicyEffect.ALLOW,
                "actions": ["read"],
            }
        ],
    }


class TestCondition:
    def test_valid_cases(self, valid_condition):
        # Basic valid condition
        condition = Condition.model_validate(valid_condition)
        assert condition.path == "attributes.role"
        assert condition.operator == ConditionOperator.EQUALS
        assert condition.value == "admin"

    def test_json_value_parsing(self, valid_condition_with_json_value):
        # Test JSON string value is parsed
        condition = Condition.model_validate(valid_condition_with_json_value)
        assert condition.value == ["read", "write"]

    def test_non_json_string_value(self):
        # Test non-JSON string remains as string
        condition_data = {
            "path": "attributes.name",
            "operator": ConditionOperator.CONTAINS,
            "value": "john doe",
        }
        condition = Condition.model_validate(condition_data)
        assert condition.value == "john doe"

    def test_numeric_value(self):
        # Test numeric values are preserved
        condition_data = {
            "path": "attributes.age",
            "operator": ConditionOperator.GREATER,
            "value": 25,
        }
        condition = Condition.model_validate(condition_data)
        assert condition.value == 25

    def test_boolean_value(self):
        # Test boolean values are preserved
        condition_data = {
            "path": "attributes.active",
            "operator": ConditionOperator.EQUALS,
            "value": True,
        }
        condition = Condition.model_validate(condition_data)
        assert condition.value is True

    def test_list_value(self):
        # Test list values are preserved
        condition_data = {
            "path": "attributes.roles",
            "operator": ConditionOperator.IN,
            "value": ["admin", "user"],
        }
        condition = Condition.model_validate(condition_data)
        assert condition.value == ["admin", "user"]

    def test_all_operators(self):
        # Test all valid operators
        operators = [
            ConditionOperator.EQUALS,
            ConditionOperator.NOT_EQUALS,
            ConditionOperator.CONTAINS,
            ConditionOperator.NOT_CONTAINS,
            ConditionOperator.STARTS_WITH,
            ConditionOperator.ENDS_WITH,
            ConditionOperator.GREATER,
            ConditionOperator.GREATER_OR_EQUAL,
            ConditionOperator.LESS,
            ConditionOperator.LESS_OR_EQUAL,
            ConditionOperator.IN,
            ConditionOperator.NOT_IN,
        ]

        for operator in operators:
            condition_data = {
                "path": "test.path",
                "operator": operator,
                "value": "test_value",
            }
            condition = Condition.model_validate(condition_data)
            assert condition.operator == operator

    def test_invalid_cases(self):
        # Missing required fields
        with pytest.raises(ValidationError):
            Condition.model_validate(
                {"path": "test.path", "operator": ConditionOperator.EQUALS}
            )

        with pytest.raises(ValidationError):
            Condition.model_validate({"path": "test.path", "value": "test"})

        with pytest.raises(ValidationError):
            Condition.model_validate(
                {"operator": ConditionOperator.EQUALS, "value": "test"}
            )

        # Invalid operator
        with pytest.raises(ValidationError):
            Condition.model_validate(
                {
                    "path": "test.path",
                    "operator": "invalid_operator",
                    "value": "test",
                }
            )


class TestRule:
    def test_valid_cases(self, valid_rule):
        # Basic valid rule
        rule = Rule.model_validate(valid_rule)
        assert rule.name == "allow-admin-access"  # Should be slugified
        assert rule.effect == PolicyEffect.ALLOW
        assert rule.actions == ["read", "write"]
        assert rule.description is None
        assert rule.principal_conditions == []
        assert rule.resource_conditions == []

    def test_rule_with_conditions(self, valid_rule_with_conditions):
        # Rule with all fields
        rule = Rule.model_validate(valid_rule_with_conditions)
        assert rule.name == "complex-rule"  # Should be slugified
        assert rule.description == "A rule with conditions"
        assert rule.effect == PolicyEffect.ALLOW
        assert len(rule.principal_conditions) == 1
        assert len(rule.resource_conditions) == 1
        assert rule.actions == ["read", "write", "delete"]

    def test_name_slugification(self):
        # Test name is properly slugified
        rule_data = {
            "name": "Allow Admin Access!!!",
            "effect": PolicyEffect.ALLOW,
            "actions": ["read"],
        }
        rule = Rule.model_validate(rule_data)
        assert rule.name == "allow-admin-access"

    def test_invalid_name_slugification(self):
        # Test that names that would result in empty slugs raise ValidationError
        invalid_names = ["!!!", "---", "🚀🎉", "   "]

        for invalid_name in invalid_names:
            rule_data = {
                "name": invalid_name,
                "effect": PolicyEffect.ALLOW,
                "actions": ["read"],
            }
            with pytest.raises(ValidationError) as exc_info:
                Rule.model_validate(rule_data)

            # Check that the error message contains the expected text
            assert "Cannot create valid slug from:" in str(exc_info.value)

    def test_actions_json_parsing(self):
        # Test actions can be parsed from JSON string
        rule_data = {
            "name": "test-rule",
            "effect": PolicyEffect.ALLOW,
            "actions": '["read", "write", "delete"]',
        }
        rule = Rule.model_validate(rule_data)
        assert rule.actions == ["read", "write", "delete"]

    def test_actions_list_preserved(self):
        # Test actions list is preserved when already a list
        rule_data = {
            "name": "test-rule",
            "effect": PolicyEffect.ALLOW,
            "actions": ["read", "write"],
        }
        rule = Rule.model_validate(rule_data)
        assert rule.actions == ["read", "write"]

    def test_both_effects(self):
        # Test both ALLOW and DENY effects
        for effect in [PolicyEffect.ALLOW, PolicyEffect.DENY]:
            rule_data = {
                "name": "test-rule",
                "effect": effect,
                "actions": ["read"],
            }
            rule = Rule.model_validate(rule_data)
            assert rule.effect == effect

    def test_invalid_cases(self):
        # Missing required fields
        with pytest.raises(ValidationError):
            Rule.model_validate({"name": "test", "effect": PolicyEffect.ALLOW})

        with pytest.raises(ValidationError):
            Rule.model_validate({"name": "test", "actions": ["read"]})

        with pytest.raises(ValidationError):
            Rule.model_validate({"effect": PolicyEffect.ALLOW, "actions": ["read"]})

        # Invalid effect
        with pytest.raises(ValidationError):
            Rule.model_validate(
                {
                    "name": "test",
                    "effect": "invalid_effect",
                    "actions": ["read"],
                }
            )

        # Invalid actions JSON
        with pytest.raises(ValidationError):
            Rule.model_validate(
                {
                    "name": "test",
                    "effect": PolicyEffect.ALLOW,
                    "actions": "invalid_json[",
                }
            )

        # Extra fields not allowed
        with pytest.raises(ValidationError):
            Rule.model_validate(
                {
                    "name": "test",
                    "effect": PolicyEffect.ALLOW,
                    "actions": ["read"],
                    "extra_field": "not_allowed",
                }
            )


class TestPolicy:
    def test_valid_cases(self, valid_policy):
        # Basic valid policy
        policy = Policy.model_validate(valid_policy)
        assert policy.name == "test-policy"  # Should be slugified
        assert policy.description == "A test policy"
        assert policy.version == "1.0"  # Default value
        assert policy.default_effect == PolicyEffect.DENY  # Default value
        assert len(policy.rules) == 1

    def test_default_values(self):
        # Test default values are applied
        policy_data = {
            "name": "Minimal Policy",
            "rules": [
                {
                    "name": "test-rule",
                    "effect": PolicyEffect.ALLOW,
                    "actions": ["read"],
                }
            ],
        }
        policy = Policy.model_validate(policy_data)
        assert policy.version == "1.0"
        assert policy.default_effect == PolicyEffect.DENY
        assert policy.description is None

    def test_custom_values(self):
        # Test custom values override defaults
        policy_data = {
            "version": "2.0",
            "name": "Custom Policy",
            "description": "Custom description",
            "default_effect": PolicyEffect.ALLOW,
            "rules": [
                {
                    "name": "test-rule",
                    "effect": PolicyEffect.ALLOW,
                    "actions": ["read"],
                }
            ],
        }
        policy = Policy.model_validate(policy_data)
        assert policy.version == "2.0"
        assert policy.default_effect == PolicyEffect.ALLOW
        assert policy.description == "Custom description"

    def test_name_slugification(self):
        # Test name is properly slugified
        policy_data = {
            "name": "My Super Complex Policy Name!!!",
            "rules": [
                {
                    "name": "test-rule",
                    "effect": PolicyEffect.ALLOW,
                    "actions": ["read"],
                }
            ],
        }
        policy = Policy.model_validate(policy_data)
        assert policy.name == "my-super-complex-policy-name"

    def test_invalid_name_slugification(self):
        # Test that names that would result in empty slugs raise ValidationError
        invalid_names = ["!!!", "---", "🚀🎉", "   "]

        for invalid_name in invalid_names:
            policy_data = {
                "name": invalid_name,
                "rules": [
                    {
                        "name": "test-rule",
                        "effect": PolicyEffect.ALLOW,
                        "actions": ["read"],
                    }
                ],
            }
            with pytest.raises(ValidationError) as exc_info:
                Policy.model_validate(policy_data)

            # Check that the error message contains the expected text
            assert "Cannot create valid slug from:" in str(exc_info.value)

    def test_multiple_rules(self):
        # Test policy with multiple rules
        policy_data = {
            "name": "Multi Rule Policy",
            "rules": [
                {
                    "name": "allow-rule",
                    "effect": PolicyEffect.ALLOW,
                    "actions": ["read"],
                },
                {
                    "name": "deny-rule",
                    "effect": PolicyEffect.DENY,
                    "actions": ["write", "delete"],
                },
            ],
        }
        policy = Policy.model_validate(policy_data)
        assert len(policy.rules) == 2
        assert policy.rules[0].name == "allow-rule"
        assert policy.rules[1].name == "deny-rule"

    def test_invalid_cases(self):
        # Missing required fields
        with pytest.raises(ValidationError):
            Policy.model_validate({"name": "test"})

        with pytest.raises(ValidationError):
            Policy.model_validate({"rules": []})

        # Invalid default_effect
        with pytest.raises(ValidationError):
            Policy.model_validate(
                {
                    "name": "test",
                    "default_effect": "invalid_effect",
                    "rules": [
                        {
                            "name": "test-rule",
                            "effect": PolicyEffect.ALLOW,
                            "actions": ["read"],
                        }
                    ],
                }
            )

        # Extra fields not allowed
        with pytest.raises(ValidationError):
            Policy.model_validate(
                {
                    "name": "test",
                    "rules": [
                        {
                            "name": "test-rule",
                            "effect": PolicyEffect.ALLOW,
                            "actions": ["read"],
                        }
                    ],
                    "extra_field": "not_allowed",
                }
            )

    def test_empty_rules_allowed(self):
        # Empty rules list should be allowed
        policy_data = {
            "name": "Empty Policy",
            "rules": [],
        }
        policy = Policy.model_validate(policy_data)
        assert policy.name == "empty-policy"
        assert policy.rules == []
        assert policy.default_effect == PolicyEffect.DENY


class TestPolicyEvaluationResult:
    def test_valid_cases(self):
        # Valid result with matched rule
        rule = Rule(
            name="test-rule",
            effect=PolicyEffect.ALLOW,
            actions=["read"],
        )
        result_data = {
            "effect": PolicyEffect.ALLOW,
            "matched_rule": rule,
            "policy_name": "test-policy",
        }
        result = PolicyEvaluationResult.model_validate(result_data)
        assert result.effect == PolicyEffect.ALLOW
        assert result.matched_rule == rule
        assert result.policy_name == "test-policy"

    def test_no_matched_rule(self):
        # Valid result without matched rule (default effect)
        result_data = {
            "effect": PolicyEffect.DENY,
            "matched_rule": None,
            "policy_name": "test-policy",
        }
        result = PolicyEvaluationResult.model_validate(result_data)
        assert result.effect == PolicyEffect.DENY
        assert result.matched_rule is None
        assert result.policy_name == "test-policy"

    def test_both_effects(self):
        # Test both ALLOW and DENY effects
        for effect in [PolicyEffect.ALLOW, PolicyEffect.DENY]:
            result_data = {
                "effect": effect,
                "policy_name": "test-policy",
            }
            result = PolicyEvaluationResult.model_validate(result_data)
            assert result.effect == effect

    def test_invalid_cases(self):
        # Missing required fields
        with pytest.raises(ValidationError):
            PolicyEvaluationResult.model_validate(
                {
                    "effect": PolicyEffect.ALLOW,
                }
            )

        with pytest.raises(ValidationError):
            PolicyEvaluationResult.model_validate(
                {
                    "policy_name": "test-policy",
                }
            )

        # Invalid effect
        with pytest.raises(ValidationError):
            PolicyEvaluationResult.model_validate(
                {
                    "effect": "invalid_effect",
                    "policy_name": "test-policy",
                }
            )
