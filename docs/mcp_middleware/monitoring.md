# Monitor & Audit

Set up comprehensive logging, monitoring, and debugging for your MCP authorization system.

## Audit Logging

Enable comprehensive audit trails to track all authorization decisions:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eunomia_mcp")

# Log messages include:
# INFO: Authorized request | MCP method: tools/call | MCP uri: mcp:tools:file_read | User-Agent: Claude
# WARNING: Authorization violation: Access denied for tools/call | MCP method: tools/call | MCP uri: mcp:tools:file_read | User-Agent: Claude
```

## Log Categories

- **INFO**: Successful authorization decisions
- **WARNING**: Authorization violations  
- **ERROR**: System errors (Eunomia server issues, etc.)

## Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.getLogger("eunomia_mcp").setLevel(logging.DEBUG)
logging.getLogger("eunomia_sdk").setLevel(logging.DEBUG)
```

## Production Logging Configuration

For production deployments, configure structured logging:

```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'mcp_audit.log',
            'formatter': 'json'
        }
    },
    'loggers': {
        'eunomia_mcp': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## Troubleshooting

### Common Issues

**Eunomia server not running**

```
ERROR: Authorization check failed: Connection refused
```

**Solution**: Start Eunomia server with `eunomia server`

**Missing policies**

```
WARNING: Authorization violation: No matching policy found
```

**Solution**: Push policies with `eunomia-mcp push policies.json`

**Invalid JSON-RPC**

```
ERROR: Invalid Request: Invalid JSON-RPC 2.0 format
```

**Solution**: Ensure MCP client sends valid JSON-RPC 2.0 requests

### Health Checks

Monitor your middleware health:

```python
from eunomia_mcp import EunomiaMcpMiddleware
import asyncio

async def health_check():
    middleware = EunomiaMcpMiddleware()
    try:
        # Test connection to Eunomia server
        result = await middleware._check_eunomia_connection()
        print(f"Eunomia server status: {'✓ Connected' if result else '✗ Disconnected'}")
    except Exception as e:
        print(f"Health check failed: {e}")

# Run health check
asyncio.run(health_check())
```

### Metrics Collection

Track authorization metrics:

```python
import time
from collections import defaultdict

class MetricsMiddleware(EunomiaMcpMiddleware):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metrics = defaultdict(int)
        self.response_times = []

    async def authorize_request(self, request):
        start_time = time.time()
        result = await super().authorize_request(request)
        
        # Record metrics
        duration = time.time() - start_time
        self.response_times.append(duration)
        self.metrics[f"status_{result.status}"] += 1
        
        return result

    def get_metrics(self):
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        return {
            "authorization_counts": dict(self.metrics),
            "avg_response_time_ms": avg_response_time * 1000,
            "total_requests": sum(self.metrics.values())
        }
```

## Next Steps

- **[Advanced Setup](advanced.md)**: Production deployment configuration
- **[Quick Start](quickstart.md)**: Return to the beginning