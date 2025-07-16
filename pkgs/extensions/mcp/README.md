# Eunomia MCP Authorization Middleware

Add **policy-based authorization** to your [MCP][mcp-docs] servers built on [FastMCP][fastmcp-docs] with minimal code changes.

## Overview

### Features

- 🔒 **Policy-Based Authorization**: Control which agents can access which MCP tools, resources, and prompts
- 📊 **Audit Logging**: Track all authorization decisions and violations
- ⚡ **FastMCP Integration**: One-line middleware integration with FastMCP servers
- 🔧 **Flexible Configuration**: JSON-based policies for complex dynamic rules with CLI tooling
- 🎯 **MCP-Aware**: Built-in understanding of MCP protocol (tools, resources, prompts)

### Architecture

The Eunomia middleware intercepts all MCP requests to your server and automatically maps MCP methods to authorization checks.

#### Listing Operations

The middleware behaves as a filter for listing operations (`tools/list`, `resources/list`, `prompts/list`), hiding to the client components that are not authorized by the defined policies.

```mermaid
sequenceDiagram
    participant MCPClient as MCP Client
    participant EunomiaMiddleware as Eunomia Middleware
    participant MCPServer as FastMCP Server
    participant EunomiaServer as Eunomia Server

    MCPClient->>EunomiaMiddleware: MCP Listing Request (e.g., tools/list)
    EunomiaMiddleware->>MCPServer: MCP Listing Request
    MCPServer-->>EunomiaMiddleware: MCP Listing Response
    EunomiaMiddleware->>EunomiaServer: Authorization Checks
    EunomiaServer->>EunomiaMiddleware: Authorization Decisions
    EunomiaMiddleware-->>MCPClient: Filtered MCP Listing Response
```

#### Execution Operations

The middleware behaves as a firewall for execution operations (`tools/call`, `resources/read`, `prompts/get`), blocking operations that are not authorized by the defined policies.

```mermaid
sequenceDiagram
    participant MCPClient as MCP Client
    participant EunomiaMiddleware as Eunomia Middleware
    participant MCPServer as FastMCP Server
    participant EunomiaServer as Eunomia Server

    MCPClient->>EunomiaMiddleware: MCP Execution Request (e.g., tools/call)
    EunomiaMiddleware->>EunomiaServer: Authorization Check
    EunomiaServer->>EunomiaMiddleware: Authorization Decision
    EunomiaMiddleware-->>MCPClient: MCP Unauthorized Error (if denied)
    EunomiaMiddleware->>MCPServer: MCP Execution Request (if allowed)
    MCPServer-->>EunomiaMiddleware: MCP Execution Response (if allowed)
    EunomiaMiddleware-->>MCPClient: MCP Execution Response (if allowed)
```

### Installation

```bash
pip install eunomia-mcp
```

## Quick Start

### Create a MCP Server with Middleware

#### Basic Integration

```python
from fastmcp import FastMCP
from eunomia_mcp import EunomiaMcpMiddleware

# Create your FastMCP server
mcp = FastMCP("Secure MCP Server 🔒")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add Eunomia authorization middleware
middleware = EunomiaMcpMiddleware()

# Create ASGI app with authorization
app = mcp.add_middleware(middleware)

if __name__ == "__main__":
    mcp.run()
```

> [!IMPORTANT]
>
> [Eunomia][eunomia-github] is a standalone server that handles the policy decisions, you must have it running alongside the MCP server.
>
> Run it in the background with Docker:
>
> ```bash
> docker run -d -p 8421:8421 --name eunomia ttommitt/eunomia-server:latest
> ```
>
> Or refer to the [Eunomia documentation][eunomia-docs-run-server] for more options.

#### Advanced Integration

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
    )
]

app = mcp.http_app(middleware=middleware)
```

### Policy Configuration

Use the `eunomia-mcp` CLI in your terminal to manage your MCP authorization policies:

#### Initialize a New Project

```bash
# Create a default policy configuration file
eunomia-mcp init

# Create policy configuration file with custom name
eunomia-mcp init --policy-file my_policies.json

# Generate both policy configuration file and a sample MCP server
eunomia-mcp init --sample
```

You can edit the created `mcp_policies.json` policy configuration file to your liking. Refer to the [templates][policy-templates] for example policies and rules.

#### Validate Policy Configuration

```bash
# Validate your policy file
eunomia-mcp validate mcp_policies.json
```

#### Push Policies to Eunomia

```bash
# Push your policy to Eunomia server
eunomia-mcp push mcp_policies.json

# Push your policy and overwrite existing ones
eunomia-mcp push mcp_policies.json --overwrite
```

> [!IMPORTANT]
> You need the Eunomia server running for the push operation.

**Workflow**: Initialize → Customize policies → Validate → Run Eunomia server → Push to Eunomia → Run MCP server

## Further Reading

### MCP Method Mappings

| MCP Method       | Resource URI           | Action | Middleware behavior                       |
| ---------------- | ---------------------- | ------ | ----------------------------------------- |
| `tools/list`     | `mcp:tools:{name}`     | `list` | Filters the server's response             |
| `resources/list` | `mcp:resources:{name}` | `list` | Filters the server's response             |
| `prompts/list`   | `mcp:prompts:{name}`   | `list` | Filters the server's response             |
| `tools/call`     | `mcp:tools:{name}`     | `call` | Blocks/forwards the request to the server |
| `resources/read` | `mcp:resources:{name}` | `read` | Blocks/forwards the request to the server |
| `prompts/get`    | `mcp:prompts:{name}`   | `get`  | Blocks/forwards the request to the server |

The middleware extracts contextual attributes from the MCP request and passes them to the decision engine; these attributes can therefore be referenced inside policies to define dynamic rules.

| Attribute        | Type              | Description                                              | Sample value           |
| ---------------- | ----------------- | -------------------------------------------------------- | ---------------------- |
| `method`         | `str`             | The MCP method                                           | `tools/list`           |
| `component_type` | `str`             | The type of component: `tools`, `resources` or `prompts` | `tools`                |
| `name`           | `str`             | The name of the component                                | `file_read`            |
| `uri`            | `str`             | The MCP URI of the component                             | `mcp:tools:file_read`  |
| `arguments`      | `dict` (Optional) | The arguments of the execution operation                 | `{"path": "file.txt"}` |

### Authentication

#### Agent Identification

Agents are identified through HTTP headers:

```http
X-Agent-ID: claude
X-User-ID: user123
User-Agent: Claude
Authorization: Bearer api-key-here
```

#### Custom Principal Extraction

You can customize principal extraction by subclassing the middleware:

```python
from eunomia_core import schemas
from eunomia_mcp import EunomiaMcpMiddleware

class CustomAuthMiddleware(EunomiaMcpMiddleware):
    def _extract_principal(self) -> schemas.PrincipalCheck:
        # Custom logic to extract principal from JWT, etc.
        return schemas.PrincipalCheck(
            uri="user:john.doe",
            attributes={"role": "admin", "department": "engineering"}
        )
```

### Logging

Enable comprehensive audit logging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eunomia_mcp")

# Authorization success
# INFO: Authorized request | MCP method: tools/call | MCP uri: mcp:tools:file_read | User-Agent: Claude

# Authorization violation
# WARNING: Authorization violation: Access denied for tools/call | MCP method: tools/call | MCP uri: mcp:tools:file_read | User-Agent: Claude
```

## Examples

### [(Sample) Planetary Weather MCP][example-planetary-weather-mcp]

### [WhatsApp MCP to Authorized Contacts][example-whatsapp-mcp]

[mcp-docs]: https://modelcontextprotocol.io
[fastmcp-docs]: https://gofastmcp.com/
[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[eunomia-docs-run-server]: https://whataboutyou-ai.github.io/eunomia/get_started/user_guide/run_server
[example-planetary-weather-mcp]: https://github.com/whataboutyou-ai/eunomia/tree/main/examples/mcp_planetary_weather
[example-whatsapp-mcp]: https://github.com/whataboutyou-ai/eunomia/tree/main/examples/mcp_whatsapp
[policy-templates]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/extensions/mcp/templates
