# Advanced Setup

Production-ready configuration and deployment options for the MCP Middleware.

## Production Configuration

Configure the middleware for production deployments:

```python
from fastmcp import FastMCP
from eunomia_mcp import create_eunomia_middleware
import os

# Production configuration
mcp = FastMCP("Production MCP Server")

middleware = [
    create_eunomia_middleware(
        eunomia_endpoint="https://eunomia.yourcompany.com",
        eunomia_api_key=os.getenv("EUNOMIA_API_KEY"),
        enable_audit_logging=True,
    )
]

app = mcp.add_middleware(middleware)

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8080,
    )
```

## Configuration Parameters

| Parameter              | Type   | Default                 | Description                            |
| ---------------------- | ------ | ----------------------- | -------------------------------------- |
| `eunomia_endpoint`     | `str`  | `http://localhost:8421` | Eunomia server URL                     |
| `eunomia_api_key`      | `str`  | `None`                  | API key (or set `WAY_API_KEY` env var) |
| `enable_audit_logging` | `bool` | `True`                  | Enable request/violation logging       |

## Environment Variables

Configure your production environment:

```bash
# Eunomia server configuration
export WAY_ENDPOINT=https://your-eunomia-server.com
export WAY_API_KEY=your-secret-api-key

# Logging level
export PYTHONLOGLEVEL=INFO

# Optional: Custom timeout settings
export EUNOMIA_TIMEOUT=30
export EUNOMIA_RETRY_COUNT=3
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV WAY_ENDPOINT=https://your-eunomia-server.com
ENV PYTHONLOGLEVEL=INFO

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "mcp_server.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8080:8080"
    environment:
      - WAY_ENDPOINT=https://eunomia.yourcompany.com
      - WAY_API_KEY=${EUNOMIA_API_KEY}
      - PYTHONLOGLEVEL=INFO
    depends_on:
      - eunomia

  eunomia:
    image: ttommitt/eunomia-server:latest
    ports:
      - "8421:8421"
    volumes:
      - eunomia_data:/app/data

volumes:
  eunomia_data:
```

## High Availability Setup

For production environments requiring high availability:

```python
from eunomia_mcp import create_eunomia_middleware

# Multiple Eunomia endpoints for failover
middleware = [
    create_eunomia_middleware(
        eunomia_endpoint="https://eunomia-primary.yourcompany.com",
        eunomia_fallback_endpoints=[
            "https://eunomia-secondary.yourcompany.com",
            "https://eunomia-tertiary.yourcompany.com"
        ],
        eunomia_api_key=os.getenv("EUNOMIA_API_KEY"),
        timeout=10,
        retry_count=3,
        enable_audit_logging=True,
    )
]
```

## Performance Optimization

### Connection Pooling

```python
from eunomia_mcp import create_eunomia_middleware

middleware = [
    create_eunomia_middleware(
        eunomia_endpoint="https://eunomia.yourcompany.com",
        connection_pool_size=20,
        max_concurrent_requests=100,
        enable_audit_logging=True,
    )
]
```

### Caching

Enable response caching for improved performance:

```python
from eunomia_mcp import create_eunomia_middleware

middleware = [
    create_eunomia_middleware(
        eunomia_endpoint="https://eunomia.yourcompany.com",
        enable_caching=True,
        cache_ttl=300,  # 5 minutes
        cache_size=1000,  # Max cached responses
    )
]
```

## Security Considerations

### TLS Configuration

Ensure secure communication:

```python
import ssl

# Custom SSL context for Eunomia connections
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

middleware = [
    create_eunomia_middleware(
        eunomia_endpoint="https://eunomia.yourcompany.com",
        ssl_context=ssl_context,
        verify_ssl=True,
    )
]
```

### API Key Rotation

Implement automatic API key rotation:

```python
import os
from datetime import datetime, timedelta

class RotatingApiKeyMiddleware(EunomiaMcpMiddleware):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_rotation = datetime.now()
        self.rotation_interval = timedelta(hours=24)

    def get_api_key(self):
        if datetime.now() - self.last_rotation > self.rotation_interval:
            # Implement your key rotation logic
            new_key = self.rotate_api_key()
            os.environ["WAY_API_KEY"] = new_key
            self.last_rotation = datetime.now()
        
        return os.getenv("WAY_API_KEY")
```

## Monitoring & Observability

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
authorization_requests = Counter('eunomia_authorization_requests_total', 'Total authorization requests', ['status'])
authorization_duration = Histogram('eunomia_authorization_duration_seconds', 'Authorization request duration')

class MonitoredMiddleware(EunomiaMcpMiddleware):
    async def authorize_request(self, request):
        with authorization_duration.time():
            result = await super().authorize_request(request)
            authorization_requests.labels(status=result.status).inc()
            return result

# Start metrics server
start_http_server(9090)
```

### Health Endpoints

```python
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("Production MCP Server")

@app.get("/health")
async def health_check():
    # Check Eunomia connectivity
    middleware = EunomiaMcpMiddleware()
    eunomia_healthy = await middleware._check_eunomia_connection()
    
    return {
        "status": "healthy" if eunomia_healthy else "unhealthy",
        "eunomia_connected": eunomia_healthy,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    # Return middleware metrics
    return middleware.get_metrics()
```

## Load Testing

Test your deployment under load:

```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1000):  # 1000 concurrent requests
            task = session.post(
                "http://localhost:8080/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "tools/list"
                }
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return responses

# Run load test
results = asyncio.run(load_test())
```

## Next Steps

- **[Monitor Access](monitoring.md)**: Set up comprehensive monitoring
- **[Quick Start](quickstart.md)**: Return to the beginning