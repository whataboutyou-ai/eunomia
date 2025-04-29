from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from eunomia_core.enums.entity import EntityType
from eunomia_core.utils import generate_uri


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
    type: Optional[EntityType] = None  # type is not required for the attributes update

    @field_validator("attributes", mode="before")
    @classmethod
    def at_least_one_attribute(cls, v: list[Attribute]) -> list[Attribute]:
        if not v:
            raise ValueError("At least one attribute must be provided")
        return v


class EntityInDb(EntityBase):
    attributes: list[AttributeInDb] = Field(..., description="Entity attributes")
    registered_at: datetime = Field(description="Time when this entity was registered")

    model_config = ConfigDict(from_attributes=True)
