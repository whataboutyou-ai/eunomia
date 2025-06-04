from typing import Any, Optional

from eunomia_core import enums, schemas


def create_attribute_condition(
    attribute_key: str,
    value: Any,
    operator: enums.ConditionOperator = enums.ConditionOperator.EQUALS,
) -> schemas.Condition:
    """
    Create a condition that matches against an entity attribute.

    Parameters
    ----------
    attribute_key: str
        The key of the attribute to match
    value: Any
        The value to match against
    operator: ConditionOperator, optional
        The operator to use for comparison

    Returns
    -------
    schemas.Condition
    A condition that can be used in a policy rule
    """
    return schemas.Condition(
        path=f"attributes.{attribute_key}", operator=operator, value=str(value)
    )


def create_simple_policy(
    name: str,
    version: str = "1.0",
    description: Optional[str] = None,
    principal_attributes: Optional[dict[str, str]] = None,
    resource_attributes: Optional[dict[str, str]] = None,
    actions: list[str] = ["access"],
    effect: enums.PolicyEffect = enums.PolicyEffect.ALLOW,
    default_effect: enums.PolicyEffect = enums.PolicyEffect.DENY,
) -> schemas.Policy:
    """
    Create a simple policy with a single rule based on attribute matching.

    Parameters
    ----------
    name: str
        Name of the policy
    version: str, optional
        Version of the policy
    description: str, optional
        Optional description
    principal_attributes: dict[str, str], optional
        Dictionary of principal attributes to match
    resource_attributes: dict[str, str], optional
        Dictionary of resource attributes to match
    actions: list[str], optional
        List of actions to match
    effect: PolicyEffect, optional
        Effect of the rule if matched
    default_effect: PolicyEffect, optional
        Default effect if no rules match

    Returns
    -------
    schemas.Policy
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
        name=name,
        effect=effect,
        principal_conditions=principal_conditions,
        resource_conditions=resource_conditions,
        actions=actions,
    )

    return schemas.Policy(
        version=version,
        name=name,
        description=description,
        rules=[rule],
        default_effect=default_effect,
    )
