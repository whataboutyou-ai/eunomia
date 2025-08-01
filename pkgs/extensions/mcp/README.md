# Eunomia MCP Authorization Middleware

Add **policy-based authorization** to your [MCP][mcp-docs] servers built on [FastMCP][fastmcp-docs] with one line of code.

> [!NOTE]
> Eunomia is the [official authorization middleware][fastmcp-eunomia-docs] of FastMCP!

## Overview

### Features

- 🔒 **Policy-Based Authorization**: Control which agents can access which MCP tools, resources, and prompts
- 📊 **Audit Logging**: Track all authorization decisions and violations
- 🔄 **Centralized Policy Enforcement**: Optionally use a remote Eunomia server for centralized policy enforcement
- ⚡ **FastMCP Integration**: One-line middleware integration with FastMCP servers
- 🔧 **Flexible Configuration**: JSON-based policies for complex dynamic rules with CLI tooling

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

## Quickstart

### Create a MCP Server with Middleware

#### Basic Integration with embedded Eunomia server

```python
from fastmcp import FastMCP
from eunomia_mcp import create_eunomia_middleware

# Create your FastMCP server
mcp = FastMCP("Secure MCP Server 🔒")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add middleware to your server
middleware = create_eunomia_middleware(policy_file="mcp_policies.json")
mcp.add_middleware(middleware)

if __name__ == "__main__":
    mcp.run()
```

#### Advanced Integration with remote Eunomia server

Configure the middleware with custom options for production deployments:

```python
from fastmcp import FastMCP
from eunomia_mcp import create_eunomia_middleware

mcp = FastMCP("Secure MCP Server 🔒")

# Configure middleware with custom options
middleware = create_eunomia_middleware(
    use_remote_eunomia=True,
    eunomia_endpoint="https://your-eunomia-server.com",
    enable_audit_logging=True,
)

mcp.add_middleware(middleware)
```

> [!IMPORTANT]
>
> You can use [Eunomia][eunomia-github] as a centralized policy decision point for multiple MCP servers,
> which is especially relevant in enterprise scenarios.
>
> You can run the Eunomia server in the background with Docker:
>
> ```bash
> docker run -d -p 8421:8421 --name eunomia ttommitt/eunomia-server:latest
> ```
>
> Or refer to [Eunomia documentation][eunomia-docs-run-server] for additional running options.

### Policy Configuration

Use the `eunomia-mcp` CLI in your terminal to manage your MCP authorization policies:

#### Creating Your First Policy

```bash
# Create a default policy configuration file
eunomia-mcp init

# Create a custom policy configuration file from your FastMCP server instance
eunomia-mcp init --custom-mcp "app.server:mcp"

# Generate both policy configuration file and a sample FastMCP server with Eunomia authorization
eunomia-mcp init --sample
```

You can edit the created `mcp_policies.json` policy configuration file to your liking. Refer to the [templates][eunomia-github-policy-templates] for example policies and rules.

#### Validating Policies

```bash
# Validate your policy file
eunomia-mcp validate mcp_policies.json
```

#### Deploying Policies

> [!NOTE]
>
> This operation is needed only if you are using a remote Eunomia server, otherwise you can skip this step.

```bash
# Push your policy to Eunomia server
eunomia-mcp push mcp_policies.json

# Push your policy and overwrite existing ones
eunomia-mcp push mcp_policies.json --overwrite
```

## Further Reading

### MCP Method Mappings

| MCP Method       | Resource URI           | Action    | Middleware behavior                       |
| ---------------- | ---------------------- | --------- | ----------------------------------------- |
| `tools/list`     | `mcp:tools:{name}`     | `list`    | Filters the server's response             |
| `tools/call`     | `mcp:tools:{name}`     | `execute` | Blocks/forwards the request to the server |
| `resources/list` | `mcp:resources:{name}` | `list`    | Filters the server's response             |
| `resources/read` | `mcp:resources:{name}` | `execute` | Blocks/forwards the request to the server |
| `prompts/list`   | `mcp:prompts:{name}`   | `list`    | Filters the server's response             |
| `prompts/get`    | `mcp:prompts:{name}`   | `execute` | Blocks/forwards the request to the server |

The middleware extracts contextual attributes from the MCP request and passes them to the decision engine; these attributes can therefore be referenced inside policies to define dynamic rules.

| Attribute        | Type              | Description                                              | Sample value           |
| ---------------- | ----------------- | -------------------------------------------------------- | ---------------------- |
| `method`         | `str`             | The MCP method                                           | `tools/list`           |
| `component_type` | `str`             | The type of component: `tools`, `resources` or `prompts` | `tools`                |
| `name`           | `str`             | The name of the component                                | `file_read`            |
| `uri`            | `str`             | The MCP URI of the component                             | `mcp:tools:file_read`  |
| `arguments`      | `dict` (Optional) | The arguments of the execution operation                 | `{"path": "file.txt"}` |

### Agent Authentication

#### Default Identification

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
from eunomia_mcp.middleware import EunomiaMcpMiddleware

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

## Documentation

Explore the detailed [documentation][eunomia-docs-mcp-middleware] for more advanced configuration and scenarios.

[mcp-docs]: https://modelcontextprotocol.io
[fastmcp-docs]: https://gofastmcp.com/
[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[eunomia-docs-run-server]: https://whataboutyou-ai.github.io/eunomia/server/pdp/run_server
[eunomia-docs-mcp-middleware]: https://whataboutyou-ai.github.io/eunomia/mcp_middleware
[example-planetary-weather-mcp]: https://github.com/whataboutyou-ai/eunomia/tree/main/examples/mcp_planetary_weather
[example-whatsapp-mcp]: https://github.com/whataboutyou-ai/eunomia/tree/main/examples/mcp_whatsapp
[eunomia-github-policy-templates]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/extensions/mcp/templates
[fastmcp-eunomia-docs]: https://gofastmcp.com/integrations/eunomia-authorization
