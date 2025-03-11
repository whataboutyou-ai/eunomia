Eunomia offers a Python client that enables users to interact with the Eunomia server.

The client allows you to register resources and principals with their metadata to the Eunomia server, as well as verify access control between principals and resources. These features simplify the integration of the Eunomia server into your Python applications.

## Installation

Install the `eunomia-sdk-python` package via pip:

```bash
pip install eunomia-sdk-python
```

## Usage

Import the `EunomiaClient` class and create an instance of it:

```python
from eunomia_sdk_python import EunomiaClient

client = EunomiaClient()
```

You can then use the client to interact with the Eunomia server:

```python
# Register a resource with metadata
resource = client.register_resource({
    "name": "sensitive_document",
    "type": "document",
    "classification": "confidential"
})

# Register a principal with metadata
principal = client.register_principal({
    "name": "user_123",
    "role": "analyst",
    "department": "research"
})

# Check if a principal has access to a resource
is_allowed = client.check_access(
    principal_id=principal["id"],
    resource_id=resource["id"]
)

# Get a list of resources a principal has access to
allowed_resources = client.allowed_resources(principal_id=principal["id"])
```

## SDK Docs

::: eunomia_sdk_python.client.EunomiaClient
