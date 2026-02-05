from typing import Any
from logging import getLogger
from eunomia_core import enums, schemas

LOGGER = getLogger("eunomia_engine")

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

def _to_set(arg: Any) -> set:
    """Helper function for converting diverse data types to sets"""
    if isinstance(arg, list):
        return set(tuple(arg))
    if isinstance(arg, str):
        return {arg}
    return set(arg)


def apply_operator(
    operator_type: enums.ConditionOperator, value: Any, target: Any
) -> bool:
    """Apply the specified operator with the value against the target."""
    if value is None or target is None:
        return False
    try:

        match operator_type:
            # Equivalency checks
            case enums.ConditionOperator.EQUALS:
                return value == target
            case enums.ConditionOperator.NOT_EQUALS:
                return value != target
            # String checks
            case enums.ConditionOperator.STARTS_WITH:
                return target.startswith(value)
            case enums.ConditionOperator.ENDS_WITH:
                return target.endswith(value)
            # Math checks
            case enums.ConditionOperator.GREATER:
                return value > target
            case enums.ConditionOperator.GREATER_OR_EQUAL:
                return value >= target
            case enums.ConditionOperator.LESS:
                return value < target
            case enums.ConditionOperator.LESS_OR_EQUAL:
                return value <= target

            # Contains and IN checks
            case enums.ConditionOperator.CONTAINS | enums.ConditionOperator.IN:
                return value in target
            case enums.ConditionOperator.NOT_CONTAINS | enums.ConditionOperator.NOT_IN:
                return value not in target

            # Subset operators: check if all items in value (set) are in target (set)
            case enums.ConditionOperator.SUBSET:
                return all(item in target for item in value)
            case enums.ConditionOperator.NOT_SUBSET:
                return all(item not in target for item in value)
            # Superset operators: check to see if the target resource is a superset of the value(s)
            case enums.ConditionOperator.SUPERSET:
                return _to_set(value).issuperset(_to_set(target))
            case enums.ConditionOperator.NOT_SUPERSET:
                return not _to_set(value).issuperset(_to_set(target))

            # Default case
            case _:
                return False

    except TypeError as err:
        LOGGER.warning(f"Unexpected target/value variable types, {err}")
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


def evaluate_rule(rule: schemas.Rule, request: schemas.CheckRequest) -> bool:
    """Evaluate if a rule matches the check request."""
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
    policy: schemas.Policy, request: schemas.CheckRequest
) -> schemas.PolicyEvaluationResult:
    """Evaluate a policy against a check request."""
    for rule in policy.rules:
        if evaluate_rule(rule, request):
            return schemas.PolicyEvaluationResult(
                effect=rule.effect, matched_rule=rule, policy_name=policy.name
            )

    # If no rules matched, return the default effect
    return schemas.PolicyEvaluationResult(
        effect=policy.default_effect, matched_rule=None, policy_name=policy.name
    )
