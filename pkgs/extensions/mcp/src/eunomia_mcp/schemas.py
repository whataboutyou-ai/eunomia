from typing import Union

from pydantic import BaseModel, field_validator
from starlette.responses import JSONResponse


class JsonRpcRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Union[dict, list, None] = None
    id: Union[int, str, None] = None

    @field_validator("jsonrpc")
    def validate_jsonrpc(cls, v):
        if v != "2.0":
            raise ValueError("expected version 2.0")
        return v

    def get_dict_params(self) -> dict:
        if isinstance(self.params, list):
            return {}
        return self.params or {}


class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Union[str, None] = None


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[int, str, None] = None
    result: Union[dict, None] = None
    error: Union[JsonRpcError, None] = None

    def as_starlette(self):
        return JSONResponse(
            content=self.model_dump(exclude_none=True),
            status_code=200,
        )
