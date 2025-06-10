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

The server provides weather information tools for Mars, Jupiter, Saturn, and Venus, but access is controlled through Eunomia policies that, as an example, only allow queries for dates in 2025.

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

### Run the Server

Start the MCP server:

```bash
python planetary_weather.py
```

The server will be available at `http://localhost:8080`. You can add it to your MCP configuration file (e.g. `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "planetary-weather": {
      "url": "http://localhost:8080/mcp/"
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

Each tool accepts a date parameter (defaults to current date) and returns descriptive weather information.

### Authorization Policies

The `mcp_policies.json` file defines two main rules:

1. **Discovery Access**: Allows all principals to list available tools, resources, and prompts
2. **Tool Execution**: Allows execution of weather tools, but only for dates starting with "2025"

```json
{
  "name": "allow-mcp-operations",
  "effect": "allow",
  "resource_conditions": [
    {
      "path": "attributes.tool_name",
      "operator": "in",
      "value": [
        "get_mars_weather",
        "get_jupiter_weather",
        "get_saturn_weather",
        "get_venus_weather"
      ]
    },
    {
      "path": "attributes.arguments.request.date",
      "operator": "startswith",
      "value": "2025"
    }
  ],
  "actions": ["execute"]
}
```

### Authorization Flow

1. Client sends MCP request to call a weather tool
2. Eunomia middleware intercepts the request
3. Request is mapped to Eunomia resource format (`mcp:tools:get_mars_weather`)
4. Eunomia policy engine evaluates access based on tool name and date parameter
5. If authorized, request proceeds to MCP server; otherwise, access is denied

[mcp-docs]: https://modelcontextprotocol.io
[fastmcp-docs]: https://gofastmcp.com/
[eunomia-mcp-github]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/extensions/mcp
[eunomia-docs-run-server]: https://whataboutyou-ai.github.io/eunomia/get_started/user_guide/run_server
