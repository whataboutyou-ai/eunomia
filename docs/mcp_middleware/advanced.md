## Centralize Policy Enforcement with a Remote Eunomia Server

The Eunomia MCP Middleware can be configured to use an **embedded Eunomia server** within the MCP server (default) or a **remote Eunomia server**.

The remote option is useful if you want to have a centralized policy decision point for multiple MCP servers,
which is especially relevant in enterprise scenarios.

!!! info

    You can run the Eunomia server in the background with Docker:

    ```bash
    docker run -d -p 8421:8421 --name eunomia ttommitt/eunomia-server:latest
    ```

    Or refer to [this documentation](../server/pdp/run_server.md) for additional running options.

Then, you can configure the middleware to use the remote Eunomia server:

```python
from eunomia_mcp import create_eunomia_middleware

middleware = create_eunomia_middleware(
    use_remote_eunomia=True,
    eunomia_endpoint="http://localhost:8421",
)
```

### Middleware Configuration

| Parameter              | Type   | Default                 | Description                                                                  |
| ---------------------- | ------ | ----------------------- | ---------------------------------------------------------------------------- |
| `policy_file`          | `str`  | `mcp_policies.json`     | Path to policy configuration JSON file, for **embedded** Eunomia server only |
| `use_remote_eunomia`   | `bool` | `False`                 | Whether to use a remote Eunomia server                                       |
| `eunomia_endpoint`     | `str`  | `http://localhost:8421` | Eunomia server URL, for **remote** Eunomia server only                       |
| `enable_audit_logging` | `bool` | `True`                  | Enable request/violation logging                                             |

## Connect to Remote MCP Servers using a Proxy

You can use the Eunomia MCP Middleware even if you are connecting to a remote MCP server that you don't control.

To do so, you can use a proxy server that will forward the requests to the remote server and apply the Eunomia MCP Middleware to the proxy server.

```python
from eunomia_mcp import create_eunomia_middleware
from fastmcp import FastMCP

config = {
    "mcpServers": {
        "default": {
            "command": "npx",
            "args": ["-y", "mcp-remote", "https://mcp.example.com/v1/sse"],
        }
    }
}

proxy = FastMCP.as_proxy(config, name="Proxy with Eunomia Middleware")

middleware = create_eunomia_middleware()
proxy.add_middleware(middleware)

if __name__ == "__main__":
    proxy.run()
```

## Logging & Monitoring

### Audit Logging

Enable comprehensive audit trails:

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

### Log Categories

- **INFO**: Successful authorization decisions
- **WARNING**: Authorization violations
- **ERROR**: System errors (Eunomia server issues, etc.)
