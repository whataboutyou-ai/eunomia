Control how agents and users are identified and authenticated by your MCP server so that you can enforce policies on them.

## Default Agent Authentication

Agents are identified through HTTP headers:

```
X-Agent-ID: claude
X-User-ID: user123
User-Agent: Claude
Authorization: Bearer api-key-here
Content-Type: application/json
```

### Principal Extraction

The middleware automatically extracts principals from these headers:

| Header                      | Principal URI  | Attributes                 |
| --------------------------- | -------------- | -------------------------- |
| `X-Agent-ID: claude`        | `agent:claude` | `{"agent_id": "claude"}`   |
| `X-User-ID: user123`        |                | `{"user_id": "user123"}`   |
| `User-Agent: Claude`        |                | `{"user_agent": "Claude"}` |
| `Authorization: Bearer xyz` |                | `{"api_key": "xyz"}`       |

## Custom Agent Authentication

### Custom Principal Extraction

For advanced authentication scenarios, you can subclass the `EunomiaMcpMiddleware` class and override the default principal extraction logic:

```python
from eunomia_core import schemas
from eunomia_mcp import EunomiaMcpMiddleware

class CustomAuthMiddleware(EunomiaMcpMiddleware):
    def _extract_principal(self) -> schemas.PrincipalCheck:
        headers = get_http_headers()
        token = headers.get("Authorization", "").replace("Bearer ", "")

        # Extract from JWT token
        if token:
            payload = decode_jwt(token)  # Your JWT decoding logic
            return schemas.PrincipalCheck(
                uri=f"user:{payload['sub']}",
                attributes={
                    "role": payload.get("role"),
                    "department": payload.get("dept")
                }
            )

        # Fallback to default
        return super()._extract_principal()

# Use custom middleware
middleware = CustomAuthMiddleware()
```

### Using Custom Authentication

Integrate your custom authentication middleware:

```python
from fastmcp import FastMCP

mcp = FastMCP("Secure MCP Server 🔒")

# Use your custom authentication
custom_middleware = CustomAuthMiddleware()
mcp.add_middleware(custom_middleware)
```
