# Customize Authentication

Control how agents and users are identified and authenticated by your MCP server.

## Default Agent Authentication

Agents are identified through HTTP headers in MCP requests:

```http
POST /mcp HTTP/1.1
X-Agent-ID: claude
X-User-ID: user123
User-Agent: Claude
Authorization: Bearer api-key-here
Content-Type: application/json
```

## Principal Extraction

The middleware automatically extracts principals from these headers:

| Header                      | Principal URI  | Attributes                 |
| --------------------------- | -------------- | -------------------------- |
| `X-Agent-ID: claude`        | `agent:claude` | `{"agent_id": "claude"}`   |
| `X-User-ID: user123`        |                | `{"user_id": "user123"}`   |
| `User-Agent: Claude`        |                | `{"user_agent": "Claude"}` |
| `Authorization: Bearer xyz` |                | `{"api_key": "xyz"}`       |

## Custom Principal Extraction

Override the default principal extraction logic for advanced authentication scenarios:

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

## JWT Token Authentication

For JWT-based authentication, extract user information from tokens:

```python
import jwt
from eunomia_core import schemas
from eunomia_mcp import EunomiaMcpMiddleware

class JWTAuthMiddleware(EunomiaMcpMiddleware):
    def __init__(self, jwt_secret: str, **kwargs):
        super().__init__(**kwargs)
        self.jwt_secret = jwt_secret

    def _extract_principal(self) -> schemas.PrincipalCheck:
        headers = get_http_headers()
        token = headers.get("Authorization", "").replace("Bearer ", "")

        if token:
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
                return schemas.PrincipalCheck(
                    uri=f"user:{payload['sub']}",
                    attributes={
                        "email": payload.get("email"),
                        "role": payload.get("role"),
                        "organization": payload.get("org")
                    }
                )
            except jwt.InvalidTokenError:
                # Handle invalid tokens
                pass

        # Fallback to default extraction
        return super()._extract_principal()
```

## API Key Authentication

For API key-based authentication systems:

```python
from eunomia_core import schemas
from eunomia_mcp import EunomiaMcpMiddleware

class ApiKeyAuthMiddleware(EunomiaMcpMiddleware):
    def __init__(self, api_key_lookup: dict, **kwargs):
        super().__init__(**kwargs)
        self.api_key_lookup = api_key_lookup

    def _extract_principal(self) -> schemas.PrincipalCheck:
        headers = get_http_headers()
        api_key = headers.get("X-API-Key") or headers.get("Authorization", "").replace("Bearer ", "")

        if api_key and api_key in self.api_key_lookup:
            user_info = self.api_key_lookup[api_key]
            return schemas.PrincipalCheck(
                uri=f"user:{user_info['user_id']}",
                attributes={
                    "tier": user_info.get("tier"),
                    "permissions": user_info.get("permissions", [])
                }
            )

        return super()._extract_principal()
```

## Using Custom Authentication

Integrate your custom authentication middleware:

```python
from fastmcp import FastMCP

mcp = FastMCP("Secure MCP Server")

# Use your custom authentication
custom_middleware = JWTAuthMiddleware(jwt_secret="your-secret-key")
app = mcp.add_middleware(custom_middleware)
```

## Next Steps

- **[Monitor Access](monitoring.md)**: Set up logging and audit trails
- **[Advanced Setup](advanced.md)**: Production deployment configuration