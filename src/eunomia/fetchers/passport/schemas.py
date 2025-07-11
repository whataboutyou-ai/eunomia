from typing import Optional

from pydantic import BaseModel


class PassportJWT(BaseModel):
    jti: str
    iat: int
    exp: int
    iss: str
    sub: str
    attr: dict = {}


class PassportIssueRequest(BaseModel):
    uri: str
    attributes: dict = {}
    ttl: Optional[int] = None


class PassportIssueResponse(BaseModel):
    passport: str
    passport_id: str
    expires_in: int
