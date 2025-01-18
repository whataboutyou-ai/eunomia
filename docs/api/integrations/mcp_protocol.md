## Overview

**Eunomia MCP Server** is an extension of the [Eunomia][main-repo] framework that connects Eunomia instruments with [MCP](https://modelcontextprotocol.io/) servers. It provides a simple way to orchestrate data governance policies (like PII detection or user access control) and seamlessly integrate them with external server processes in the MCP ecosystem.

With Eunomia MCP Server, you can:

- **Enforce data governance** on top of LLM or other text-based pipelines.
- **Orchestrate multiple servers** that communicate via the MCP framework.

---

## Get Started

### Installation

```bash
git clone https://github.com/whataboutyou-ai/eunomia-MCP-server.git
```

---

## Basic Usage

Eunomia MCP Server uses the same "instrument" concept as [Eunomia][main-repo]. By defining your set of instruments in an `Orchestra`, you can apply data governance policies to text streams that flow through your MCP-based servers.

Below is a simplified example of how to define application settings and run the MCP server with [uv](https://docs.astral.sh/uv/).

```python
"""
Example Settings for MCP Orchestra Server
=========================================
This example shows how we can combine Eunomia with a web-browser-mcp-server
(https://github.com/blazickjp/web-browser-mcp-server).
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from eunomia.orchestra import Orchestra
from eunomia.instruments import IdbacInstrument, PiiInstrument


class Settings(BaseSettings):
    """
    Application settings class for MCP orchestra server using pydantic_settings.

    Attributes:
        APP_NAME (str): Name of the application
        APP_VERSION (str): Current version of the application
        LOG_LEVEL (str): Logging level (default: "info")
        MCP_SERVERS (dict): Servers to be connected
        ORCHESTRA (Orchestra): Orchestra class from Eunomia to define data governance policies
    """

    APP_NAME: str = "mcp-server_orchestra"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "info"
    MCP_SERVERS: dict = {
        "web-browser-mcp-server": {
            "command": "uv",
            "args": [
                "tool",
                "run",
                "web-browser-mcp-server"
            ],
            "env": {
                "REQUEST_TIMEOUT": "30"
            }
        }
    }
    ORCHESTRA: Orchestra = Orchestra(
        instruments=[
            PiiInstrument(entities=["EMAIL_ADDRESS", "PERSON"], edit_mode="replace"),
            # You can add more instruments here
            # e.g., IdbacInstrument(), etc.
        ]
    )
```

### Running the Server

Once your settings are defined, you can run the MCP Orchestra server by pointing `uv` to the directory containing your server code, for example:

```bash
uv --directory "path/to/server/" run orchestra_server
```

This will:

1. Load the settings from `.env` or environment variables.
2. Launch the **Eunomia MCP Server** to handle requests and orchestrate your external MCP server(s).
3. Apply Eunomia instruments (like `PiiInstrument`) to the incoming text, ensuring data governance policies are automatically enforced.

---

## Documentation

For more detailed usage, advanced configuration, and additional instruments, check out the following resources:

- [Eunomia Documentation][docs]: Learn more about the core Eunomia framework.
- [Main Eunomia Repository][main-repo]: See the source code and examples.
- [MCP Documentation][mcp-docs]: Explore the Model Context Protocol specification and ecosystem.

---


[whataboutyou-website]: https://whataboutyou.ai
[docs]: https://whataboutyou-ai.github.io/eunomia/
[discord]: https://discord.gg/TyhGZtzg3G
[main-repo]: https://github.com/WhatAboutYou-ai/eunomia
[mcp-docs]: https://modelcontextprotocol.io/