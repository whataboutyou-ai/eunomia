# Eunomia MCP Authorization Middleware

Add **policy-based authorization** to your [MCP][mcp-docs] servers built on [FastMCP][fastmcp-docs] with minimal code changes.

## Features

- 🔒 **Policy-Based Authorization**: Control which agents can access which MCP resources and tools
- 📊 **Audit Logging**: Track all authorization decisions and violations
- ⚡ **FastMCP Integration**: One-line middleware integration with FastMCP servers
- 🔧 **Flexible Configuration**: JSON-based policies with support for complex rules
- 🎯 **MCP-Aware**: Built-in understanding of MCP protocol (tools, resources, prompts)

## Installation

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

> [!IMPORTANT]
>
> [Eunomia][eunomia-github] is a standalone server that handles the policy decisions, you must have it running alongside the MCP server.
>
> Install the `eunomia-ai` package and run it in the background with
>
> ```bash
> eunomia server
> ```
>
> Or refer to the [Eunomia documentation][eunomia-docs-run-server] for more options.

### Advanced Integration

Configure the middleware with custom options for production deployments:

```python
from fastmcp import FastMCP
from eunomia_mcp import create_eunomia_middleware

mcp = FastMCP("Secure MCP Server 🔒")

# Configure middleware with custom options
middleware = [
    create_eunomia_middleware(
        eunomia_endpoint="https://your-eunomia-server.com",
        eunomia_api_key="your-api-key",
        enable_audit_logging=True,
        bypass_methods=["initialize", "notifications/*"]
    )
]

app = mcp.http_app(middleware=middleware)
```

## Policy Configuration

Use the `eunomia-mcp` CLI to manage your MCP authorization policies:

### Initialize a New Project

```bash
# Create a default policy configuration file
eunomia-mcp init

# Create policy configuration file with custom name
eunomia-mcp init --policy-file my_policies.json

# Generate both policy configuration file and a sample MCP server
eunomia-mcp init --sample
```

You can now edit the policy configuration file to your liking.

### Validate Policy Configuration

```bash
# Validate your policy file
eunomia-mcp validate mcp_policies.json
```

### Push Policies to Eunomia

```bash
# Push your policy to Eunomia server
eunomia-mcp push mcp_policies.json

# Push your policy and overwrite existing ones
eunomia-mcp push mcp_policies.json --overwrite
```

> [!IMPORTANT]
> You need the Eunomia server running for the push operation.

**Workflow**: Initialize → Customize policies → Validate → Run Eunomia server → Push to Eunomia → Run MCP server

## How It Works

### 1. Request Interception

The middleware intercepts all JSON-RPC 2.0 requests to your MCP server:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "file_read",
    "arguments": { "path": "/private/secrets.txt" }
  },
  "id": 1
}
```

### 2. Authorization Check

Requests are mapped to Eunomia resources and checked against policies:

- **Principal**: Extracted from request headers (`X-Agent-ID`, `X-User-ID`, `Authorization`)
- **Resource**: Mapped from MCP method and parameters (e.g., `mcp:tools:file_read`)
- **Action**: Derived from MCP method (e.g., `execute` for `tools/call`)

### 3. Response

- ✅ **Authorized**: Request proceeds to MCP server
- ❌ **Denied**: JSON-RPC error response returned

## MCP Method Mappings

| MCP Method       | Resource URI         | Action    | Notes                    |
| ---------------- | -------------------- | --------- | ------------------------ |
| `tools/list`     | `mcp:tools`          | `access`  | List available tools     |
| `tools/call`     | `mcp:tools:{name}`   | `execute` | Execute specific tool    |
| `resources/list` | `mcp:resources`      | `access`  | List available resources |
| `resources/read` | `mcp:resource:{uri}` | `read`    | Read specific resource   |
| `prompts/list`   | `mcp:prompts`        | `access`  | List available prompts   |
| `prompts/get`    | `mcp:prompt:{name}`  | `read`    | Get specific prompt      |

## Authentication

### Agent Identification

Agents are identified through HTTP headers:

```http
X-Agent-ID: claude
X-User-ID: user123
Authorization: Bearer api-key-here
```

### Custom Principal Extraction

You can customize principal extraction by subclassing the middleware:

```python
from eunomia_mcp import EunomiaMcpMiddleware

class CustomAuthMiddleware(EunomiaMcpMiddleware):
    def _extract_principal_info(self, request):
        # Custom logic to extract principal from JWT, etc.
        return {
            "uri": "user:john.doe",
            "attributes": {"role": "admin", "department": "engineering"}
        }
```

## Error Responses

Authorization failures return standard JSON-RPC errors:

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

## Logging

Enable comprehensive audit logging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eunomia_mcp")

# Authorization success
# INFO: Authorized MCP request: tools/call | Client: 192.168.1.100

# Authorization violation
# WARNING: Authorization violation: Access denied for tools/call | Method: tools/call | Client: 192.168.1.100
```

[mcp-docs]: https://modelcontextprotocol.io
[fastmcp-docs]: https://gofastmcp.com/
[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[eunomia-docs-run-server]: https://whataboutyou-ai.github.io/eunomia/get_started/user_guide/run_server
