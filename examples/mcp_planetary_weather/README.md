# Planetary Weather MCP Server with Eunomia Authorization

This example demonstrates how to build a secure [MCP][mcp-docs] (Model Context Protocol) server using [FastMCP][fastmcp-docs] with the [Eunomia MCP Authorization Middleware][eunomia-mcp-github]. The server provides weather information for planets in our solar system with fine-grained access controls.

> [!NOTE]
> This example is a reference implementation and fully functional. It can be used as a starting point for adding authorization to your own MCP server. Simply swap your FastMCP server and edit the policy to match your needs.

## Overview

The example shows how to:

- Create an MCP server using FastMCP with multiple tools
- Add policy-based authorization using Eunomia middleware
- Define access control policies that restrict tool usage based on parameters
- Set up audit logging for authorization decisions

The server provides weather information tools for Mars, Jupiter, Saturn, and Venus, but access is controlled through Eunomia policies that demonstrate different authorization patterns based on tool names and time parameters.

## Usage

### Prerequisites

You need to have the Eunomia server running alongside the MCP server. Install and start it:

```bash
pip install eunomia-ai
eunomia server
```

Or refer to the [Eunomia documentation][eunomia-docs-run-server] for other deployment options.

### Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configure Policies

The example includes a pre-configured policy file (`mcp_policies.json`). Push it to your Eunomia server:

```bash
eunomia-mcp push mcp_policies.json
```

### Configure the MCP Server

You can add it to your MCP configuration file (e.g. `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "planetary-weather": {
      "command": "python",
      "args": ["planetary_weather.py"]
    }
  }
}
```

## How It Works

### MCP Server

The server implements four weather tools:

- `get_mars_weather` - Get weather conditions on Mars
- `get_jupiter_weather` - Get weather conditions on Jupiter
- `get_saturn_weather` - Get weather conditions on Saturn
- `get_venus_weather` - Get weather conditions on Venus

Each tool accepts a `time` parameter (either "day" or "night", defaults to "day") and returns descriptive weather information.

### Authorization Policies

The `mcp_policies.json` file defines three rules with different access patterns:

1. **Full Access**: Allows listing and calling for Mars and Venus weather tools
2. **List Only**: Allows listing Jupiter weather tool but not calling it
3. **Restricted Access**: Allows calling Jupiter weather tool only when the time parameter is "night"

### Access Patterns

- **Mars & Venus**: Can be listed and called with any time parameter
- **Jupiter**: Can be listed, but can only be called when time is "night"
- **Saturn**: Not mentioned in policy (implicitly denied for all operations) - will not be seen by the MCP client

[mcp-docs]: https://modelcontextprotocol.io
[fastmcp-docs]: https://gofastmcp.com/
[eunomia-mcp-github]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/extensions/mcp
[eunomia-docs-run-server]: https://whataboutyou-ai.github.io/eunomia/get_started/user_guide/run_server
