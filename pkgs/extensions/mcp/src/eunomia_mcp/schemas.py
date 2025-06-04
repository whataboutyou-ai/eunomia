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


class JsonRpcErrorResponse(BaseModel):
    jsonrpc: str = "2.0"
    error: JsonRpcError
    id: Union[int, str, None] = None

    def as_starlette_json_response(self):
        return JSONResponse(
            content=self.model_dump(exclude_none=True),
            status_code=200,
        )
