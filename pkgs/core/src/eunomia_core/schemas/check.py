from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from eunomia_core.enums.entity import EntityType
from eunomia_core.schemas.entity import Attribute


class EntityCheck(BaseModel):
    uri: Optional[str] = Field(
        default=None, description="Unique identifier for the entity"
    )
    attributes: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Entity attributes"
    )
    type: EntityType = Field(..., description="Type of entity")

    @field_validator("attributes", mode="before")
    @classmethod
    def from_list(cls, v: list[Attribute] | dict) -> dict[str, Any]:
        if isinstance(v, list) and all(isinstance(attr, Attribute) for attr in v):
            return {attr.key: attr.value for attr in v}
        elif isinstance(v, list):
            return {attr["key"]: attr["value"] for attr in v}
        return v

    @model_validator(mode="after")
    def either_uri_or_attributes(self) -> "EntityCheck":
        if not self.uri and not self.attributes:
            raise ValueError("Either 'uri' or non-empty 'attributes' must be provided")
        return self


class ResourceCheck(EntityCheck):
    type: Literal[EntityType.resource] = EntityType.resource


class PrincipalCheck(EntityCheck):
    type: Literal[EntityType.principal] = EntityType.principal


class CheckRequest(BaseModel):
    principal: PrincipalCheck = Field(
        ..., description="The principal performing the action"
    )
    resource: ResourceCheck = Field(..., description="The resource being acted on")
    action: str = Field(
        default="access", description="The action being performed on the resource"
    )


class CheckResponse(BaseModel):
    allowed: bool = Field(..., description="Whether the action is allowed")
    reason: Optional[str] = Field(None, description="The reason for the decision")
