This section contains the documentation for the main package containing the Eunomia server.

The Eunomia server is a standalone service to handle the authorization logic of your AI Agent. The server can be self-hosted, exposing a REST API to your application.

## Installation

```bash
pip install eunomia-ai
```

## Usage

Run the server with:

```bash
eunomia server
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
