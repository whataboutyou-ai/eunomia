import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from eunomia_core.enums import EntityType


class AttributeCreate(BaseModel):
    key: str = Field(..., description="Attribute key")
    value: str = Field(..., description="Attribute value")


class Attribute(AttributeCreate):
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


class EntityCreate(EntityBase):
    uri: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Optional unique identifier for the entity, if not provided, the server will generate a random UUID",
    )
    attributes: list[AttributeCreate] | dict = Field(
        default_factory=list, description="Entity attributes"
    )

    @field_validator("attributes", mode="before")
    @classmethod
    def validate_attributes(cls, v):
        if isinstance(v, dict):
            return [AttributeCreate(key=k, value=str(val)) for k, val in v.items()]
        return v


class Entity(EntityBase):
    uri: str = Field(..., description="Unique identifier for the entity")
    attributes: list[Attribute] = Field(..., description="Entity attributes")
    registered_at: datetime = Field(description="Time when this entity was registered")

    class Config:
        from_attributes = True


class Resource(Entity):
    type: Literal[EntityType.resource, EntityType.any] = EntityType.resource


class Principal(Entity):
    type: Literal[EntityType.principal, EntityType.any] = EntityType.principal
