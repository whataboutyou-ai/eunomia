from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from eunomia_core.enums import EntityType


class AttributeRequest(BaseModel):
    key: str = Field(..., description="Attribute key")
    value: str = Field(..., description="Attribute value")


class AttributeResponse(AttributeRequest):
    updated_at: datetime = Field(
        description="Time when this attribute was last updated"
    )
    registered_at: datetime = Field(
        description="Time when this attribute was first registered"
    )

    class Config:
        from_attributes = True


class EntityBase(BaseModel):
    type: EntityType = Field(..., description="Type of entity")


class EntityRequest(EntityBase):
    uri: Optional[str] = Field(
        default=None,
        description="Optional unique identifier for the entity",
    )
    attributes: Optional[list[AttributeRequest] | dict] = Field(
        default_factory=list,
        description="Entity attributes, either as a list of key, value pairs or a dictionary",
    )

    @model_validator(mode="after")
    def ensure_uri_or_attributes(self) -> "EntityRequest":
        if not self.uri and not self.attributes:
            raise ValueError("Either 'uri' or non-empty 'attributes' must be provided")
        return self

    @field_validator("attributes", mode="before")
    @classmethod
    def validate_attributes(cls, v):
        if isinstance(v, dict):
            return [AttributeRequest(key=k, value=str(val)) for k, val in v.items()]
        return v


class EntityResponse(EntityBase):
    uri: str = Field(..., description="Unique identifier for the entity")
    attributes: list[AttributeResponse] = Field(..., description="Entity attributes")
    registered_at: datetime = Field(description="Time when this entity was registered")

    class Config:
        from_attributes = True


class ResourceRequest(EntityRequest):
    """
    Resource entity.
    The type is always overridden to "resource", although it can accept "any" as input.
    """

    type: Literal[EntityType.resource, EntityType.any] = EntityType.resource

    @field_validator("type", mode="after")
    @classmethod
    def normalize_type(cls, v):
        return EntityType.resource


class PrincipalRequest(EntityRequest):
    """
    Principal entity.
    The type is always overridden to "principal", although it can accept "any" as input.
    """

    type: Literal[EntityType.principal, EntityType.any] = EntityType.principal

    @field_validator("type", mode="after")
    @classmethod
    def normalize_type(cls, v):
        return EntityType.principal
