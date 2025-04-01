# Eunomia SDK for Python

This package allows you to integrate [Eunomia][eunomia-github] inside your Python application, providing a client to interact with the Eunomia server.

## Installation

Install the `eunomia-sdk-python` package via pip:

```bash
pip install eunomia-sdk-python
```

## Usage

Create an instance of the `EunomiaClient` class to interact with the Eunomia server.

```python
from eunomia_sdk_python import EunomiaClient

client = EunomiaClient()
```

You can then call any server endpoint through the client. For example, you can check the access of a principal to a resource:

```python
has_access = client.check_access(
    principal_attributes={"role": "admin"},
    resource_attributes={"type": "confidential"},
)

print(f"Has access: {has_access}")
```

## Documentation

For detailed usage, check out the SDK's [documentation][docs].

[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[docs]: https://whataboutyou-ai.github.io/eunomia/api/sdks/python/
