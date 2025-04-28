from typing import Any, Optional

from eunomia.engine import schemas
from eunomia.engine.enums import ConditionOperator, PolicyEffect


def create_attribute_condition(
    attribute_key: str,
    value: Any,
    operator: ConditionOperator = ConditionOperator.EQUALS,
) -> schemas.Condition:
    """
    Create a condition that matches against an entity attribute.

    Args:
        attribute_key: The key of the attribute to match
        value: The value to match against
        operator: The operator to use for comparison

    Returns:
        A condition that can be used in a policy rule
    """
    return schemas.Condition(
        path=f"attributes.{attribute_key}", operator=operator, value=str(value)
    )


def create_simple_policy(
    name: str,
    description: Optional[str] = None,
    principal_attributes: Optional[dict[str, str]] = None,
    resource_attributes: Optional[dict[str, str]] = None,
    effect: PolicyEffect = PolicyEffect.ALLOW,
    default_effect: PolicyEffect = PolicyEffect.DENY,
) -> schemas.Policy:
    """
    Create a simple policy with a single rule based on attribute matching.

    Args:
        name: Name of the policy
        description: Optional description
        principal_attributes: Dictionary of principal attributes to match
        resource_attributes: Dictionary of resource attributes to match
        effect: Effect of the rule if matched
        default_effect: Default effect if no rules match

    Returns:
        A policy with a single rule
    """
    principal_conditions: list[schemas.Condition] = []
    resource_conditions: list[schemas.Condition] = []

    if principal_attributes:
        for key, value in principal_attributes.items():
            principal_conditions.append(create_attribute_condition(key, value))

    if resource_attributes:
        for key, value in resource_attributes.items():
            resource_conditions.append(create_attribute_condition(key, value))

    rule = schemas.Rule(
        description=f"Automatically generated rule for {name}",
        effect=effect,
        principal_conditions=principal_conditions,
        resource_conditions=resource_conditions,
        action="access",
    )

    return schemas.Policy(
        name=name, description=description, rules=[rule], default_effect=default_effect
    )
