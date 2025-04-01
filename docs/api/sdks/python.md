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
resource = client.register_entity(
    type="resource",
    attributes={
        "name": "sensitive_document",
        "type": "document",
        "classification": "confidential"}
    )

# Register a principal with metadata
principal = client.register_entity(
    type="principal",
    attributes={
        "name": "user_123",
        "role": "analyst",
        "department": "research"}
    )

# Check if a principal has access to a resource
has_access = client.check_access(
    principal_uri=principal.uri,
    resource_uri=resource.uri
)
```

## SDK Docs

::: eunomia_sdk_python.client.EunomiaClient
