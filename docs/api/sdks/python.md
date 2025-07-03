Eunomia offers a Python client that enables users to interact with the Eunomia server.

The client allows you to register resources and principals with their metadata to the Eunomia server, as well as verify permissions of principals performing actions on resources. These features simplify the integration of the Eunomia server into your Python applications.

## Installation

Install the `eunomia-sdk` package via pip:

```bash
pip install eunomia-sdk
```

## Usage

### Standard API

Use the standard API for authorization checks in your application:

```python
from eunomia_sdk import EunomiaClient

client = EunomiaClient(endpoint="http://localhost:8000")

# Check if a principal has permissions to perform an action on a resource
response = client.check(
    principal_uri="user:123",
    resource_uri="document:456",
    action="read",
)

print(f"Is allowed: {response.allowed}")
```

### Admin API Usage

Use the admin API for server configuration and entity management:

```python
from eunomia_sdk import EunomiaClient

# For admin API usage authentication via API key might be required
client = EunomiaClient(
    endpoint="http://localhost:8000",
    api_key="your-admin-api-key"  # or set WAY_API_KEY environment variable
)

# Register a resource with metadata
resource = client.register_entity(
    type="resource",
    uri="document:456",
    attributes={
        "name": "sensitive_document",
        "type": "document",
        "classification": "confidential",
    },
)

# Register a principal with metadata
principal = client.register_entity(
    type="principal",
    uri="user:123",
    attributes={
        "name": "user_123",
        "role": "analyst",
        "department": "research",
    },
)
```

## Docs

::: eunomia_sdk.client.EunomiaClient
