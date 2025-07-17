# Quick Start

Get your MCP server secured with authorization in under 5 minutes.

## Prerequisites

- A FastMCP server (or ready to create one)
- Python 3.8+ environment

## Step 1: Install the Middleware

```bash
pip install eunomia-mcp
```

## Step 2: Add Middleware to Your Server

### Basic Integration

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

## Step 3: Start Eunomia Server

The middleware requires a running Eunomia server to make policy decisions:

```bash
# Install and start Eunomia server
pip install eunomia-ai
eunomia server
```

Refer to the [Eunomia server documentation](../get_started/user_guide/run_server.md) for additional configuration options.

## Step 4: Test Your Setup

Run your MCP server and test that authorization is working:

```bash
python your_mcp_server.py
```

Your server now has authorization middleware! By default, all requests will be denied until you configure policies.

## Next Steps

- **[Configure Policies](policies.md)**: Define who can access what
- **[Authentication Setup](authentication.md)**: Customize how agents are identified
- **[Monitoring](monitoring.md)**: Set up logging and audit trails