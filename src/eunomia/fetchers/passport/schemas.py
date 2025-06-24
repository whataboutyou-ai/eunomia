from pydantic import BaseModel


class PassportJWT(BaseModel):
    jti: str
    iat: int
    exp: int
    sub: str
    attr: dict = {}
