---
title: Eunomia Server Docs
---

Eunomia Server is a self-hosted platform that enables seamless integration with clients through SDKs. It manages and stores metadata for principals and resources, and uses this information to define and enforce policies with an underlying OPA server.

The server comprises the following key components:

| Server Component | Description                                                                                                                                                  | Jump to                                      |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| **Server**     | Contains the core logic for the server, including functions to register new resources.                                                                       | [:material-arrow-right: Page](server.md)      |
| **Config**     | Offers a customizable settings class to configure the server (e.g., server URL, parameters, etc.).                                                            | [:material-arrow-right: Page](config.md)   |
| **APIs**       | Handles interactions between clients and the SDK.                                                                                                           | [:material-arrow-right: Page](apis.md)   |
| **DB**         | Instantiates a SQLite database to store metadata for principals and resources, with the flexibility to switch to other database systems as needed.          | [:material-arrow-right: Page](db.md)      |
| **Engine**     | Deploys an OPA server engine to evaluate policies at runtime and provides helper functions for defining policies in Rego.                                       | [:material-arrow-right: Page](engine.md)   |

 