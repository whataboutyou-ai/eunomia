from typing import Any, Literal, Optional

from pydantic import BaseModel


class McpAttributes(BaseModel):
    method: Literal[
        "tools/list",
        "prompts/list",
        "resources/list",
        "tools/call",
        "resources/read",
        "prompts/get",
    ]
    component_type: Literal["tools", "prompts", "resources"]
    name: str
    uri: str
    arguments: Optional[dict[str, Any]] = None
