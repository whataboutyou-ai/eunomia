from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, field_validator


class ResourceCreate(BaseModel):
    metadatas: dict[str, Any]
    content: Optional[str] = None


class ResourceMetadata(BaseModel):
    key: str
    value: str

    class Config:
        from_attributes = True


class Resource(ResourceCreate):
    id: int
    registered_at: datetime

    @field_validator("metadatas", mode="before")
    def metadatas_to_dict(cls, metadatas: Union[dict, list]):
        """Custom validator to convert metadatas into a dictionary"""
        if isinstance(metadatas, dict):
            # If it's already a dictionary, return it as is
            return metadatas
        metadatas_dict = {}
        for m in metadatas:
            metadata = ResourceMetadata.model_validate(m)
            metadatas_dict[metadata.key] = metadata.value
        return metadatas_dict

    class Config:
        from_attributes = True


class PrincipalCreate(BaseModel):
    metadatas: dict[str, Any]


class PrincipalMetadata(BaseModel):
    key: str
    value: str

    class Config:
        from_attributes = True


class Principal(PrincipalCreate):
    id: int
    registered_at: datetime

    @field_validator("metadatas", mode="before")
    def metadatas_to_dict(cls, metadatas: Union[dict, list]):
        """Custom validator to convert metadatas into a dictionary"""
        if isinstance(metadatas, dict):
            # If it's already a dictionary, return it as is
            return metadatas
        metadatas_dict = {}
        for m in metadatas:
            metadata = PrincipalMetadata.model_validate(m)
            metadatas_dict[metadata.key] = metadata.value
        return metadatas_dict

    class Config:
        from_attributes = True
