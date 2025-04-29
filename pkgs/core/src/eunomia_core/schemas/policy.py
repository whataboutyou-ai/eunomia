from pydantic import BaseModel, Field

from eunomia_core.schemas.access import AccessRequest


class Policy(BaseModel):
    rules: list[AccessRequest] = Field(..., description="List of access rules")
