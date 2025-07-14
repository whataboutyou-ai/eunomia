# WhatsApp MCP with Eunomia Authorization Middleware

This example demonstrates how to secure a WhatsApp MCP server using Eunomia MCP Middleware to prevent accidental data sharing with unauthorized contacts.

## Overview

The WhatsApp MCP server from [lharries/whatsapp-mcp][whatsapp-mcp-github] allows you to interact with WhatsApp directly from your MCP client (like Cursor or Claude Desktop). However, without proper safeguards, you might accidentally share sensitive code or information with the wrong contacts. This example shows how to use Eunomia MCP Middleware to implement authorization policies that restrict message sending to only approved recipients.

### Architecture

This setup involves three running components:

1. **Go WhatsApp Bridge**: Connects to WhatsApp's web API
2. **Eunomia Authorization Server**: Manages and enforces authorization policies
3. **Python MCP Server with Middleware**: Serves MCP tools with authorization checks

## Step-by-step Implementation

### Prerequisites

- Python 3.10+
- uv (Python package manager)
- Go
- Cursor IDE or Claude Desktop

### Step 1: Set up the WhatsApp MCP Server

1. **Clone the WhatsApp MCP repository:**

   ```bash
   git clone https://github.com/lharries/whatsapp-mcp.git
   cd whatsapp-mcp
   ```

2. **Start the WhatsApp bridge:**

   ```bash
   cd whatsapp-bridge
   go run main.go
   ```

   On first run, you'll need to scan a QR code with your WhatsApp mobile app to authenticate.

3. **Keep this terminal running** - the Go bridge needs to stay active to maintain the WhatsApp connection.

### Step 2: Install Required Python Packages

In a new terminal, navigate to your working directory and install the required packages:

```bash
uv pip install eunomia-ai eunomia-mcp fastmcp
```

### Step 3: Prepare the MCP Server Files

1. **Update the import in `whatsapp-mcp-server/main.py` to use FastMCP 2.0:**

   ```diff
   - from mcp.server.fastmcp import FastMCP
   + from fastmcp import FastMCP
   ```

2. **Create main_authz.py with the Eunomia middleware:**

   ```python
   from eunomia_mcp import create_eunomia_middleware

   from main import mcp

   middleware = create_eunomia_middleware()
   app = mcp.add_middleware(middleware)

   if __name__ == "__main__":
      mcp.run(transport="http", host="0.0.0.0", port=8088)
   ```

### Step 4: Configure MCP Client Connection

Create or update your MCP configuration file (e.g., for Cursor `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "whatsapp": {
      "url": "http://localhost:8088/mcp/"
    }
  }
}
```

### Step 5: Configure Authorization Policies

Use the provided `mcp_policies.json` as a reference to implement your authorization rules.

> [!Important]
> Replace `PHONE_NUMBER_1`, `PHONE_NUMBER_2`, `PHONE_NUMBER_3` with the actual phone numbers you want to allow message sending to; with country code but no + or other symbols, or a JID (e.g., `123456789@s.whatsapp.net` or a group JID like `123456789@g.us`).

### Step 6: Start the Eunomia Authorization Server

In a new terminal, start the Eunomia server:

```bash
eunomia server
```

Keep this terminal running - the authorization server needs to be active to enforce policies.

### Step 7: Deploy the Authorization Policy

In another terminal, push your policy configuration to the Eunomia server:

```bash
eunomia-mcp push mcp_policies.json
```

You should see a confirmation that the policy has been successfully deployed.

### Step 8: Start the MCP Server with Middleware

In a new terminal, start the Python MCP server with authorization middleware:

```bash
uv run main_authz.py
```

### Step 9: Connect Your MCP Client

Restart your client (Cursor or Claude Desktop) to load the new MCP configuration. You should now see WhatsApp as an available integration with authorization protection.

## Post-Setup

### Running System Overview

You should now have three processes running:

1. **Terminal 1**: `go run main.go` (WhatsApp bridge)
2. **Terminal 2**: `eunomia server` (Authorization server)
3. **Terminal 3**: `uv run main_authz.py` (MCP server with middleware)

### Testing the Setup

Try asking your client to:

- List your WhatsApp contacts (should work)
- Send a message to an approved phone number (should work)
- Send a message to a non-approved contact (should be blocked)

### Customizing Authorization Policies

You can modify `mcp_policies.json` to customize the authorization behavior:

- **Add more approved phone numbers**: Add them to the `value` array in the `restrict-send-tools` rule
- **Allow additional operations**: Modify the `attributes.name`'s `value` array with additional tool names
- **Add time-based restrictions**: Use additional conditions with date/time operators
- **Implement user-based policies**: Add `attributes.user_id` in the principal conditions

After modifying the policy, redeploy it:

```bash
eunomia-mcp push mcp_policies.json
```

### Security Benefits

With this setup, you get:

- **Prevent accidental data sharing**: Messages can only be sent to pre-approved contacts
- **Audit trail**: All authorization decisions are logged by Eunomia
- **Fine-grained control**: Separate read and write permissions for different operations
- **Policy as code**: Authorization rules are version-controlled and reproducible

For more information on how to use the Eunomia MCP Middleware visit the extension's [GitHub][eunomia-mcp-github] page.

[whatsapp-mcp-github]: https://github.com/lharries/whatsapp-mcp
[eunomia-mcp-github]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/extensions/mcp
