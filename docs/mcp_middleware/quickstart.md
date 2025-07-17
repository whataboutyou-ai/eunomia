Get your MCP server secured with authorization in under 5 minutes.

## Step 1: Install the Middleware

```bash
pip install eunomia-mcp
```

## Step 2: Add Middleware to Your Server

```python title="server.py"
from fastmcp import FastMCP
from eunomia_mcp import EunomiaMcpMiddleware

mcp = FastMCP("Secure FastMCP Server 🔒")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

middleware = EunomiaMcpMiddleware()
mcp.add_middleware(middleware)

if __name__ == "__main__":
    mcp.run()
```

## Step 3: Start Eunomia Server

The middleware requires a running Eunomia server to make policy decisions.

Run it in the background with Docker:

```bash
docker run -d -p 8000:8000 ttommitt/eunomia-server:latest
```

Or refer to the [Eunomia server documentation](../get_started/user_guide/run_server.md) for additional configuration options.

## Step 4: Start Your Server

You can now run your MCP server normally:

```bash
python server.py
```

Your server now has authorization middleware! By default, all requests will be denied until you **[configure policies](policies.md)**.
