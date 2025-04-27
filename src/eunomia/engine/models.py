from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class PolicyEffect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class ConditionOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class Condition(BaseModel):
    path: str = Field(
        ...,
        description="Path to the attribute in dot notation (e.g., 'principal.attributes.role')",
    )
    operator: ConditionOperator = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Value to compare against")


class PolicyRule(BaseModel):
    description: Optional[str] = Field(
        None, description="Human-readable description of the rule"
    )
    effect: PolicyEffect = Field(..., description="Effect when the rule matches")
    principal_conditions: list[Condition] = Field(
        default_factory=list, description="Conditions applied to principal"
    )
    resource_conditions: list[Condition] = Field(
        default_factory=list, description="Conditions applied to resource"
    )
    action: str = Field(..., description="Action being evaluated")


class Policy(BaseModel):
    name: str = Field(..., description="Name of the policy")
    description: Optional[str] = Field(
        None, description="Human-readable description of the policy"
    )
    rules: list[PolicyRule] = Field(..., description="list of rules to evaluate")
    default_effect: PolicyEffect = Field(
        PolicyEffect.DENY, description="Default effect if no rules match"
    )


class PolicyEvaluationResult(BaseModel):
    effect: PolicyEffect = Field(
        ..., description="The resulting effect (allow or deny)"
    )
    matched_rule: Optional[PolicyRule] = Field(
        None, description="The rule that determined the effect, if any"
    )
    policy_name: str = Field(
        ..., description="The name of the policy that was evaluated"
    )
