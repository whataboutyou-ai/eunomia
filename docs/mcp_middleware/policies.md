Define fine-grained access control rules for your MCP server using JSON-based policies and CLI tools.

## Policy Management CLI

Use the `eunomia-mcp` CLI in your terminal to manage your MCP authorization policies.

### Creating Your First Policy

```bash
# Create a default policy configuration file
eunomia-mcp init

# Create policy configuration file with custom name
eunomia-mcp init --policy-file my_policies.json

# Generate both policy configuration file and a sample MCP server
eunomia-mcp init --sample
```

You can edit the created `mcp_policies.json` policy configuration file to your liking. Refer to the [templates][eunomia-github-policy-templates] for example policies and rules.

### Validating Policies

```bash
# Validate your policy file
eunomia-mcp validate mcp_policies.json
```

### Deploying Policies

```bash
# Push your policy to Eunomia server
eunomia-mcp push mcp_policies.json

# Push your policy and overwrite existing ones
eunomia-mcp push mcp_policies.json --overwrite
```

!!! info

    You need the Eunomia server running for the push operation.

Workflow:

1. **Initialize**: `eunomia-mcp init`
2. **Customize**: Edit generated policy file
3. **Validate**: `eunomia-mcp validate mcp_policies.json`
4. **Start Server**: `eunomia server`
5. **Deploy**: `eunomia-mcp push mcp_policies.json`
6. **Run**: Run your MCP server with middleware

## MCP Context Extraction

### Methods Mapping

The middleware automatically maps MCP methods to authorization checks:

| MCP Method       | Resource URI           | Action | Middleware behavior                       |
| ---------------- | ---------------------- | ------ | ----------------------------------------- |
| `tools/list`     | `mcp:tools:{name}`     | `list` | Filters the server's response             |
| `resources/list` | `mcp:resources:{name}` | `list` | Filters the server's response             |
| `prompts/list`   | `mcp:prompts:{name}`   | `list` | Filters the server's response             |
| `tools/call`     | `mcp:tools:{name}`     | `call` | Blocks/forwards the request to the server |
| `resources/read` | `mcp:resources:{name}` | `read` | Blocks/forwards the request to the server |
| `prompts/get`    | `mcp:prompts:{name}`   | `get`  | Blocks/forwards the request to the server |

### Contextual Attributes

The middleware extracts contextual attributes from the MCP request and passes them to the decision engine; these attributes can therefore be referenced inside policies to define dynamic rules.

| Attribute        | Type              | Description                                              | Sample value           |
| ---------------- | ----------------- | -------------------------------------------------------- | ---------------------- |
| `method`         | `str`             | The MCP method                                           | `tools/list`           |
| `component_type` | `str`             | The type of component: `tools`, `resources` or `prompts` | `tools`                |
| `name`           | `str`             | The name of the component                                | `file_read`            |
| `uri`            | `str`             | The MCP URI of the component                             | `mcp:tools:file_read`  |
| `arguments`      | `dict` (Optional) | The arguments of the execution operation                 | `{"path": "file.txt"}` |

You now have an MCP server with authorization that enforces customized policies. Explore [agent authentication](authentication.md) to further secure your server.

[eunomia-github-policy-templates]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/extensions/mcp/templates
