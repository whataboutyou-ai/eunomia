from datetime import datetime
from typing import Literal, Optional

from eunomia_core.enums import EntityType
from eunomia_core.utils import generate_uri
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Attribute(BaseModel):
    key: str = Field(..., description="Attribute key")
    value: str = Field(..., description="Attribute value")


class AttributeInDb(Attribute):
    updated_at: datetime = Field(
        description="Time when this attribute was last updated"
    )
    registered_at: datetime = Field(
        description="Time when this attribute was first registered"
    )

    model_config = ConfigDict(from_attributes=True)


class EntityBase(BaseModel):
    uri: str = Field(..., description="Unique identifier for the entity")
    attributes: list[Attribute] = Field(..., description="Entity attributes")
    type: EntityType = Field(..., description="Type of entity")

    @field_validator("attributes", mode="before")
    @classmethod
    def from_dict(cls, v: list[Attribute] | dict) -> list[Attribute]:
        if isinstance(v, dict):
            return [Attribute(key=k, value=str(val)) for k, val in v.items()]
        return v

    @field_validator("attributes", mode="after")
    @classmethod
    def unique_attribute_keys(cls, v: list[Attribute]) -> list[Attribute]:
        keys = {}
        for i, attr in enumerate(v):
            if attr.key in keys:
                raise ValueError(
                    f"Duplicate attribute key: '{attr.key}' at positions {keys[attr.key]} and {i}"
                )
            keys[attr.key] = i
        return v


class EntityCreate(EntityBase):
    uri: Optional[str] = Field(
        default_factory=lambda: generate_uri(),
        description="Unique identifier for the entity, generated if not provided",
    )

    @field_validator("attributes", mode="before")
    @classmethod
    def at_least_one_attribute(cls, v: list[Attribute]) -> list[Attribute]:
        if not v:
            raise ValueError("At least one attribute must be provided")
        return v

    @field_validator("uri", mode="after")
    @classmethod
    def enforce_uri(cls, v: str | None) -> str:
        if v is None:
            return generate_uri()
        return v


class EntityUpdate(EntityBase):
    type: EntityType = EntityType.any  # type is not required for the attributes update

    @field_validator("attributes", mode="before")
    @classmethod
    def at_least_one_attribute(cls, v: list[Attribute]) -> list[Attribute]:
        if not v:
            raise ValueError("At least one attribute must be provided")
        return v


class EntityAccess(EntityBase):
    uri: Optional[str] = Field(
        default=None, description="Unique identifier for the entity"
    )
    attributes: Optional[list[Attribute]] = Field(
        default_factory=list, description="Entity attributes"
    )

    @model_validator(mode="after")
    def either_uri_or_attributes(self) -> "EntityAccess":
        if not self.uri and not self.attributes:
            raise ValueError("Either 'uri' or non-empty 'attributes' must be provided")
        return self


class EntityInDb(EntityBase):
    attributes: list[AttributeInDb] = Field(..., description="Entity attributes")
    registered_at: datetime = Field(description="Time when this entity was registered")

    model_config = ConfigDict(from_attributes=True)


class ResourceAccess(EntityAccess):
    type: Literal[EntityType.resource, EntityType.any] = EntityType.resource

    # The type is always overridden to "resource", although it can accept "any" as input.
    @field_validator("type", mode="after")
    @classmethod
    def override_type(cls, v):
        return EntityType.resource


class PrincipalAccess(EntityAccess):
    type: Literal[EntityType.principal, EntityType.any] = EntityType.principal

    # The type is always overridden to "principal", although it can accept "any" as input.
    @field_validator("type", mode="after")
    @classmethod
    def override_type(cls, v):
        return EntityType.principal


class AccessRequest(BaseModel):
    principal: PrincipalAccess = Field(
        ..., description="The principal requesting access"
    )
    resource: ResourceAccess = Field(..., description="The resource being accessed")
    action: Literal["allow"] = Field(
        default="allow",
        description="Action to be performed on the resource. "
        "Currently only 'allow' is supported.",
    )


class Policy(BaseModel):
    rules: list[AccessRequest] = Field(..., description="List of access rules")
