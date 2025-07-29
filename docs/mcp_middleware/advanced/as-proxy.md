# Authorize Remote MCP Servers using a Proxy

You can use the Eunomia MCP Middleware even if you are connecting to **remote MCP servers** that you don't control.

To do so, you can use a **proxy MCP server** that will forward the requests to the remote servers and apply the Eunomia MCP Middleware within the proxy server.

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
