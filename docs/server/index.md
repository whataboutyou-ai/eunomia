---
title: Eunomia Server Docs
---

The Eunomia server is a standalone service to handle the authorization logic of your AI Agent. The server can be self-hosted, exposing a REST API to your application.

Interactions from your application to the Eunomia server are held in two different phases:

- **Configuration**: use Eunomia to define and configure the authorization policies. The server allows you to store metadata for principals and resources which can then be used to define the policies.
- **Enforcement**: your application can communicate with the server to check if a given principal has access to a specific resource. At runtime, the server retrieves the metadata stored in the previous phase for the given principal and resource and then evaluate them against the defined policies.

The Eunomia server is built on top of [Open Policy Agent (OPA)][opa-website] which Eunomia will try to install automatically if it is not already present in your system.

Explore the [available SDKs](../sdks/index.md#available-sdks) for an easier integration of Eunomia into your application.

## Running the Server

The server can be served locally with:

```bash
fastapi dev src/eunomia/api/main.py
```

## Components

The Eunomia server is composed of the following components:

| Component  | Description                                                                                          | Jump to                                  |
| ---------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **APIs**   | Exposes endpoints for applications to interact with the server.                                      | [:material-arrow-right: Page](apis.md)   |
| **Config** | Offers a customizable settings class to configure the server.                                        | [:material-arrow-right: Page](config.md) |
| **DB**     | Instantiates a SQL database to store policies and principals/resources metadata. Defaults to SQLite. | [:material-arrow-right: Page](db.md)     |
| **Engine** | Handles the communication with the OPA policy engine server.                                         | [:material-arrow-right: Page](engine.md) |
| **Server** | Contains the core logic for the server.                                                              | [:material-arrow-right: Page](server.md) |

[opa-website]: https://www.openpolicyagent.org/
