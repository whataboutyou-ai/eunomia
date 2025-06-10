The Eunomia MCP Authorization Middleware provides **policy-based authorization** for [Model Context Protocol (MCP)][mcp-docs] servers built with [FastMCP][fastmcp-docs]. It enables you to secure your MCP servers with fine-grained access control policies with minimal code changes.

## Overview

### Features

- 🔒 **Policy-Based Authorization**: Control which agents can access specific MCP resources and tools
- 📊 **Comprehensive Audit Logging**: Track all authorization decisions and security violations
- ⚡ **Zero-Configuration Integration**: One-line middleware setup with FastMCP servers
- 🔧 **Flexible Policy Management**: JSON-based policies with CLI tooling for management
- 🎯 **MCP Protocol Aware**: Built-in understanding of MCP methods (tools, resources, prompts)
- 🚀 **Production Ready**: Configurable endpoints, API keys, and bypass rules

### Architecture

The middleware operates as a transparent authorization layer that:

1. **Intercepts** JSON-RPC 2.0 requests to your MCP server
2. **Extracts** principal information from request headers
3. **Maps** MCP methods to Eunomia resources and actions
4. **Authorizes** requests against your defined policies
5. **Logs** all authorization decisions for audit trails

## Installation

Install the extension via pip:

```bash
pip install eunomia-mcp
```

## Quick Start

### Basic Integration

```python
from fastmcp import FastMCP
from eunomia_mcp import create_eunomia_middleware

# Create your FastMCP server
mcp = FastMCP("Secure MCP Server 🔒")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add Eunomia authorization middleware
middleware = [create_eunomia_middleware()]

# Create ASGI app with authorization
app = mcp.http_app(middleware=middleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Start Eunomia Server

The middleware requires a running Eunomia server to make policy decisions:

```bash
# Install and start Eunomia server
pip install eunomia-ai
eunomia server
```

Refer to the [Eunomia server documentation](../../get_started/user_guide/run_server.md) for additional configuration options.

## Configuration

### Middleware Options

Configure the middleware for production deployments:

```python
from eunomia_mcp import create_eunomia_middleware

middleware = [
    create_eunomia_middleware(
        eunomia_endpoint="https://your-eunomia-server.com",
        eunomia_api_key="your-api-key",
        enable_audit_logging=True,
        bypass_methods=["initialize", "notifications/*", "ping"]
    )
]
```

#### Parameters

| Parameter              | Type        | Default                             | Description                            |
| ---------------------- | ----------- | ----------------------------------- | -------------------------------------- |
| `eunomia_endpoint`     | `str`       | `http://localhost:8000`             | Eunomia server URL                     |
| `eunomia_api_key`      | `str`       | `None`                              | API key (or set `WAY_API_KEY` env var) |
| `enable_audit_logging` | `bool`      | `True`                              | Enable request/violation logging       |
| `bypass_methods`       | `list[str]` | `["initialize", "notifications/*"]` | Methods to skip authorization          |

### Environment Variables

```bash
# Eunomia server configuration
export WAY_ENDPOINT=https://your-eunomia-server.com
export WAY_API_KEY=your-secret-api-key

# Logging level
export PYTHONLOGLEVEL=INFO
```

## Policy Management CLI

The extension includes a CLI tool for managing MCP authorization policies:

### Initialize Project

Create a new policy configuration:

```bash
# Create default policy file
eunomia-mcp init

# Create with custom name
eunomia-mcp init --policy-file my_policies.json

# Generate policy + sample MCP server
eunomia-mcp init --sample
```

### Validate Policies

Verify your policy configuration:

```bash
# Validate policy syntax
eunomia-mcp validate mcp_policies.json
```

### Deploy Policies

Push policies to your Eunomia server:

```bash
# Push policies to server
eunomia-mcp push mcp_policies.json

# Overwrite existing policies
eunomia-mcp push mcp_policies.json --overwrite
```

### Development Workflow

1. **Initialize**: `eunomia-mcp init --sample`
2. **Customize**: Edit generated policy file
3. **Validate**: `eunomia-mcp validate policies.json`
4. **Start Server**: `eunomia server`
5. **Deploy**: `eunomia-mcp push policies.json`
6. **Test**: Run your MCP server with middleware

## Authentication & Authorization

### MCP Method Mappings

MCP JSON-RPC methods are mapped to Eunomia resources:

| MCP Method       | Resource URI          | Action    | Description              |
| ---------------- | --------------------- | --------- | ------------------------ |
| `tools/list`     | `mcp:tools`           | `access`  | List available tools     |
| `tools/call`     | `mcp:tools:{name}`    | `execute` | Execute specific tool    |
| `resources/list` | `mcp:resources`       | `access`  | List available resources |
| `resources/read` | `mcp:resource:{uri}`  | `read`    | Read specific resource   |
| `prompts/list`   | `mcp:prompts`         | `access`  | List available prompts   |
| `prompts/get`    | `mcp:prompt:{name}`   | `read`    | Get specific prompt      |
| Other            | `mcp:method:{method}` | `access`  | Any other method         |

### Agent Authentication

Agents are identified through HTTP headers:

```http
POST /mcp HTTP/1.1
X-Agent-ID: claude
X-User-ID: user123
Authorization: Bearer your-api-key
Content-Type: application/json
```

#### Principal Extraction

The middleware extracts principals as follows:

| Header                      | Principal URI  | Attributes               |
| --------------------------- | -------------- | ------------------------ |
| `X-Agent-ID: claude`        | `agent:claude` | `{"agent_id": "claude"}` |
| `X-User-ID: user123`        |                | `{"user_id": "user123"}` |
| `Authorization: Bearer xyz` |                | `{"api_key": "xyz"}`     |

#### Custom Principal Extraction

Override the default principal extraction logic:

```python
from eunomia_mcp import EunomiaMcpMiddleware
from starlette.requests import Request

class CustomAuthMiddleware(EunomiaMcpMiddleware):
    def _extract_principal_info(self, request: Request) -> tuple[str, dict]:
        # Extract from JWT token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token:
            payload = decode_jwt(token)  # Your JWT decoding logic
            return f"user:{payload['sub']}", {
                "role": payload.get("role"),
                "department": payload.get("dept")
            }

        # Fallback to default
        return super()._extract_principal_info(request)

# Use custom middleware
from starlette.middleware import Middleware
middleware = [Middleware(CustomAuthMiddleware, eunomia_client=client)]
```

## Error Handling

### Authorization Errors

Denied requests return JSON-RPC errors:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Unauthorized",
    "data": "Access denied for tools/call"
  },
  "id": 1
}
```

### Common Error Codes

| Code     | Message         | Cause                   |
| -------- | --------------- | ----------------------- |
| `-32700` | Parse error     | Invalid JSON in request |
| `-32600` | Invalid Request | Malformed JSON-RPC 2.0  |
| `-32603` | Unauthorized    | Authorization denied    |

## Logging & Monitoring

### Audit Logging

Enable comprehensive audit trails:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eunomia_mcp")

# Log messages include:
# INFO: Authorized MCP request: tools/call | Client: 192.168.1.100
# WARNING: Authorization violation: Access denied | Method: tools/call | Client: 192.168.1.100
```

### Log Categories

- **INFO**: Successful authorization decisions
- **WARNING**: Authorization violations
- **ERROR**: System errors (Eunomia server issues, etc.)

## Advanced Usage

### Production Deployment

```python
from fastmcp import FastMCP
from eunomia_mcp import create_eunomia_middleware

# Production configuration
mcp = FastMCP("Production MCP Server")

middleware = [
    create_eunomia_middleware(
        eunomia_endpoint="https://eunomia.yourcompany.com",
        eunomia_api_key=os.getenv("EUNOMIA_API_KEY"),
        enable_audit_logging=True,
        bypass_methods=["initialize", "capabilities", "notifications/*"]
    )
]

app = mcp.http_app(middleware=middleware)

# Deploy with production ASGI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        workers=4,
        log_level="info"
    )
```

## Troubleshooting

### Common Issues

**Eunomia server not running**

```
ERROR: Authorization check failed: Connection refused
```

Solution: Start Eunomia server with `eunomia server`

**Missing policies**

```
WARNING: Authorization violation: No matching policy found
```

Solution: Push policies with `eunomia-mcp push policies.json`

**Invalid JSON-RPC**

```
ERROR: Invalid Request: Invalid JSON-RPC 2.0 format
```

Solution: Ensure MCP client sends valid JSON-RPC 2.0 requests

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger("eunomia_mcp").setLevel(logging.DEBUG)
logging.getLogger("eunomia_sdk_python").setLevel(logging.DEBUG)
```

## API Reference

:::eunomia_mcp.create_eunomia_middleware

[mcp-docs]: https://modelcontextprotocol.io
[fastmcp-docs]: https://gofastmcp.com/
