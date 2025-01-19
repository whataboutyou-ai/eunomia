The [Eunomia MCP Server][eunomia-mcp-github] is a library developed by [What About You][whataboutyou-website] to integrate with Anthropic's [Model Context Protocol (MCP)][mcp-docs] framework. This library allows to serve Eunomia as an MCP server and to connect it to any external server in the MCP ecosystem.


## Get Started

### Installation

```bash
git clone https://github.com/whataboutyou-ai/eunomia-MCP-server.git
```

### Basic Usage

Eunomia MCP Server uses the same "instrument" concept as Eunomia. By defining your set of instruments in an `Orchestra`, you can apply data governance policies to text streams that flow through your MCP-based servers.

Below is a simplified example of how to define application settings and run the MCP server with [uv][uv-docs].

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


[eunomia-mcp-github]: https://github.com/whataboutyou-ai/eunomia-MCP-server
[whataboutyou-website]: https://whataboutyou.ai
[mcp-docs]: https://modelcontextprotocol.io/
[uv-docs]: https://docs.astral.sh/uv/
