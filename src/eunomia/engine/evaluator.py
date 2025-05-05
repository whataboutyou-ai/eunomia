from typing import Any

from eunomia_core import enums, schemas


def get_attribute_value(obj: Any, path: str) -> Any:
    """Extract a value from an object using dot notation path."""
    components = path.split(".")
    current = obj

    for component in components:
        if hasattr(current, component):
            current = getattr(current, component)
        elif isinstance(current, dict) and component in current:
            current = current[component]
        elif (
            isinstance(current, list)
            and component.isdigit()
            and int(component) < len(current)
        ):
            current = current[int(component)]
        else:
            return None

        if current is None:
            return None

    return current


def apply_operator(
    operator_type: enums.ConditionOperator, value: Any, target: Any
) -> bool:
    """Apply the specified operator with the value against the target."""
    if value is None or target is None:
        return False

    if isinstance(value, str) and isinstance(target, str):
        if operator_type == enums.ConditionOperator.EQUALS:
            return value == target
        elif operator_type == enums.ConditionOperator.NOT_EQUALS:
            return value != target
        elif operator_type == enums.ConditionOperator.CONTAINS:
            return value in target
        elif operator_type == enums.ConditionOperator.STARTS_WITH:
            return target.startswith(value)
        elif operator_type == enums.ConditionOperator.ENDS_WITH:
            return target.endswith(value)

    # For non-string types, only equality operators make sense
    if operator_type == enums.ConditionOperator.EQUALS:
        return value == target
    elif operator_type == enums.ConditionOperator.NOT_EQUALS:
        return value != target

    return False


def evaluate_condition(condition: schemas.Condition, obj: Any) -> bool:
    """Evaluate a single condition against an object."""
    target_value = get_attribute_value(obj, condition.path)
    return apply_operator(condition.operator, condition.value, target_value)


def evaluate_conditions(conditions: list[schemas.Condition], obj: Any) -> bool:
    """Evaluate a list of conditions against an object (AND logic)."""
    if not conditions:
        return True

    return all(evaluate_condition(condition, obj) for condition in conditions)


def evaluate_rule(rule: schemas.Rule, request: schemas.AccessRequest) -> bool:
    """Evaluate if a rule matches the access request."""
    # Check action match
    if request.action not in rule.actions:
        return False

    # Evaluate principal conditions
    principal_match = evaluate_conditions(rule.principal_conditions, request.principal)
    if not principal_match:
        return False

    # Evaluate resource conditions
    resource_match = evaluate_conditions(rule.resource_conditions, request.resource)
    if not resource_match:
        return False

    return True


def evaluate_policy(
    policy: schemas.Policy, request: schemas.AccessRequest
) -> schemas.PolicyEvaluationResult:
    """Evaluate a policy against an access request."""
    for rule in policy.rules:
        if evaluate_rule(rule, request):
            return schemas.PolicyEvaluationResult(
                effect=rule.effect, matched_rule=rule, policy_name=policy.name
            )

    # If no rules matched, return the default effect
    return schemas.PolicyEvaluationResult(
        effect=policy.default_effect, matched_rule=None, policy_name=policy.name
    )
