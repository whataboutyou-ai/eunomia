from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from eunomia_core.enums.entity import EntityType
from eunomia_core.schemas.entity import Attribute


class EntityAccess(BaseModel):
    uri: Optional[str] = Field(
        default=None, description="Unique identifier for the entity"
    )
    attributes: Optional[dict[str, str]] = Field(
        default_factory=dict, description="Entity attributes"
    )
    type: EntityType = Field(..., description="Type of entity")

    @field_validator("attributes", mode="before")
    @classmethod
    def from_list(cls, v: list[Attribute] | dict) -> dict[str, str]:
        if isinstance(v, list) and all(isinstance(attr, Attribute) for attr in v):
            return {attr.key: attr.value for attr in v}
        elif isinstance(v, list):
            return {attr["key"]: attr["value"] for attr in v}
        return v

    @model_validator(mode="after")
    def either_uri_or_attributes(self) -> "EntityAccess":
        if not self.uri and not self.attributes:
            raise ValueError("Either 'uri' or non-empty 'attributes' must be provided")
        return self


class ResourceAccess(EntityAccess):
    type: Literal[EntityType.resource] = EntityType.resource


class PrincipalAccess(EntityAccess):
    type: Literal[EntityType.principal] = EntityType.principal


class AccessRequest(BaseModel):
    principal: PrincipalAccess = Field(
        ..., description="The principal requesting access"
    )
    resource: ResourceAccess = Field(..., description="The resource being accessed")
    action: str = Field(
        default="access", description="Action to be performed on the resource"
    )
