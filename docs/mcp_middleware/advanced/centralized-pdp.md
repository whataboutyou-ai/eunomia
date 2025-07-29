# Centralize Policy Enforcement with a Remote Eunomia Server

The Eunomia MCP Middleware can be configured to use an **embedded Eunomia server** within the MCP server (default) or a **remote Eunomia server**.

The remote option is useful if you want to have a **centralized policy decision point** for multiple MCP servers,
which is especially relevant in enterprise scenarios.

!!! info

    You can run the Eunomia server in the background with Docker:

    ```bash
    docker run -d -p 8421:8421 --name eunomia ttommitt/eunomia-server:latest
    ```

    Or refer to [this documentation](../../server/pdp/run_server.md) for additional running options.

Then, you can configure the middleware to use the remote Eunomia server:

```python
from eunomia_mcp import create_eunomia_middleware

middleware = create_eunomia_middleware(
    use_remote_eunomia=True,
    eunomia_endpoint="http://localhost:8421",
)
```

## Middleware Configuration

The `create_eunomia_middleware` function accepts the following parameters:

| Parameter              | Type   | Default                 | Description                                                                  |
| ---------------------- | ------ | ----------------------- | ---------------------------------------------------------------------------- |
| `policy_file`          | `str`  | `mcp_policies.json`     | Path to policy configuration JSON file, for **embedded** Eunomia server only |
| `use_remote_eunomia`   | `bool` | `False`                 | Whether to use a remote Eunomia server                                       |
| `eunomia_endpoint`     | `str`  | `http://localhost:8421` | Eunomia server URL, for **remote** Eunomia server only                       |
| `enable_audit_logging` | `bool` | `True`                  | Enable request/violation logging                                             |
