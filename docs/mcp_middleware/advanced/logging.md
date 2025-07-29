## Audit Logging

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

## Log Categories

- **INFO**: Successful authorization decisions
- **WARNING**: Authorization violations
- **ERROR**: System errors (Eunomia server issues, etc.)
