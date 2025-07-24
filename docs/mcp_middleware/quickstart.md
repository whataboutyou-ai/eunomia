Get your MCP server secured with authorization in under 5 minutes.

## Step 1: Install the Middleware

```bash
pip install eunomia-mcp
```

## Step 2: Add Middleware to Your Server

```python title="server.py"
from fastmcp import FastMCP
from eunomia_mcp import create_eunomia_middleware

# Create your FastMCP server
mcp = FastMCP("Secure MCP Server 🔒")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add middleware to your server
middleware = create_eunomia_middleware()
mcp.add_middleware(middleware)

if __name__ == "__main__":
    mcp.run()
```

## Step 3: Use Your Server

You can now run your MCP server normally:

```bash
python server.py
```

Your server now has authorization middleware! By default, all requests will be denied until you **[configure policies](policies.md)**.
