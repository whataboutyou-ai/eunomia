## Advanced Configuration

### Middleware Options

Configure the middleware with custom configuration (e.g., for production deployments):

```python
from eunomia_mcp import create_eunomia_middleware

middleware = create_eunomia_middleware(
    eunomia_endpoint="https://your-eunomia-server.com",
    eunomia_api_key="your-api-key",
    enable_audit_logging=True,
)
```

#### Parameters

| Parameter              | Type   | Default                 | Description                            |
| ---------------------- | ------ | ----------------------- | -------------------------------------- |
| `eunomia_endpoint`     | `str`  | `http://localhost:8421` | Eunomia server URL                     |
| `eunomia_api_key`      | `str`  | `None`                  | API key (or set `WAY_API_KEY` env var) |
| `enable_audit_logging` | `bool` | `True`                  | Enable request/violation logging       |

#### Environment Variables

```bash
# Eunomia server configuration
export WAY_API_KEY=your-secret-api-key

# Logging level
export PYTHONLOGLEVEL=INFO
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

## Troubleshooting

### Common Issues

**Eunomia server not running**

```
ERROR: Authorization check failed: Connection refused
```

Solution: Start Eunomia server with `eunomia server`

**Missing policies**

```
WARNING: Authorization violation: No matching policy found
```

Solution: Push policies with `eunomia-mcp push policies.json`

**Invalid JSON-RPC**

```
ERROR: Invalid Request: Invalid JSON-RPC 2.0 format
```

Solution: Ensure MCP client sends valid JSON-RPC 2.0 requests
