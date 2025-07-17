# Configure Policies

Define fine-grained access control rules for your MCP server using JSON-based policies and CLI tools.

## Policy Management CLI

Use the `eunomia-mcp` CLI to manage your MCP authorization policies:

## Creating Your First Policy

### Initialize a New Project

```bash
# Create a default policy configuration file
eunomia-mcp init

# Create policy configuration file with custom name
eunomia-mcp init --policy-file my_policies.json

# Generate both policy configuration file and a sample MCP server
eunomia-mcp init --sample
```

You can edit the created `mcp_policies.json` policy configuration file to your liking. Refer to the [templates][policy-templates] for example policies and rules.

### Development Workflow

1. **Initialize**: `eunomia-mcp init --sample`
2. **Customize**: Edit generated policy file
3. **Validate**: `eunomia-mcp validate policies.json`
4. **Start Server**: `eunomia server`
5. **Deploy**: `eunomia-mcp push policies.json`
6. **Test**: Run your MCP server with middleware

## Validating Policies

```bash
# Validate your policy file
eunomia-mcp validate mcp_policies.json
```

## Deploying Policies

```bash
# Push your policy to Eunomia server
eunomia-mcp push mcp_policies.json

# Push your policy and overwrite existing ones
eunomia-mcp push mcp_policies.json --overwrite
```

!!! info
    You need the Eunomia server running for the push operation.

## MCP Method Mappings

The middleware automatically maps MCP methods to authorization checks:

| MCP Method       | Resource URI           | Action | Middleware behavior                       |
| ---------------- | ---------------------- | ------ | ----------------------------------------- |
| `tools/list`     | `mcp:tools:{name}`     | `list` | Filters the server's response             |
| `resources/list` | `mcp:resources:{name}` | `list` | Filters the server's response             |
| `prompts/list`   | `mcp:prompts:{name}`   | `list` | Filters the server's response             |
| `tools/call`     | `mcp:tools:{name}`     | `call` | Blocks/forwards the request to the server |
| `resources/read` | `mcp:resources:{name}` | `read` | Blocks/forwards the request to the server |
| `prompts/get`    | `mcp:prompts:{name}`   | `get`  | Blocks/forwards the request to the server |

## Available Context Attributes

The middleware extracts contextual attributes from MCP requests that can be referenced in your policies:

| Attribute        | Type              | Description                                              | Sample value           |
| ---------------- | ----------------- | -------------------------------------------------------- | ---------------------- |
| `method`         | `str`             | The MCP method                                           | `tools/list`           |
| `component_type` | `str`             | The type of component: `tools`, `resources` or `prompts` | `tools`                |
| `name`           | `str`             | The name of the component                                | `file_read`            |
| `uri`            | `str`             | The MCP URI of the component                             | `mcp:tools:file_read`  |
| `arguments`      | `dict` (Optional) | The arguments of the execution operation                 | `{"path": "file.txt"}` |

## Next Steps

- **[Customize Authentication](authentication.md)**: Configure how agents are identified
- **[Monitor Access](monitoring.md)**: Set up logging and audit trails

[policy-templates]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/extensions/mcp/templates