import json
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from eunomia_core.enums.policy import ConditionOperator, PolicyEffect


class Condition(BaseModel):
    path: str = Field(
        ...,
        description="Path to the attribute in dot notation (e.g., 'attributes.role')",
    )
    operator: ConditionOperator = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Value to compare against")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("value", mode="before")
    @classmethod
    def parse_json(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v


class Rule(BaseModel):
    name: str = Field(..., description="Name of the rule")
    effect: PolicyEffect = Field(..., description="Effect when the rule matches")
    principal_conditions: list[Condition] = Field(
        default_factory=list, description="Conditions applied to principal"
    )
    resource_conditions: list[Condition] = Field(
        default_factory=list, description="Conditions applied to resource"
    )
    actions: list[str] = Field(..., description="All actions evaluated by the rule")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("actions", mode="before")
    @classmethod
    def parse_json(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, str):
            return json.loads(v)
        return v


class Policy(BaseModel):
    version: str = Field("1.0", description="Version of the policy")
    name: str = Field(..., description="Name of the policy")
    description: Optional[str] = Field(
        None, description="Human-readable description of the policy"
    )
    rules: list[Rule] = Field(..., description="list of rules to evaluate")
    default_effect: PolicyEffect = Field(
        PolicyEffect.DENY, description="Default effect if no rules match"
    )

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class PolicyEvaluationResult(BaseModel):
    effect: PolicyEffect = Field(..., description="The resulting effect")
    matched_rule: Optional[Rule] = Field(
        None, description="The rule that determined the effect, if any"
    )
    policy_name: str = Field(
        ..., description="The name of the policy that was evaluated"
    )
