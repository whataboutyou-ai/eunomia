# This is a sample file, you should clone the repo at
# https://github.com/lharries/whatsapp-mcp
# and use the main.py file from there

# Exchange the fastmcp import as follows:
# - from mcp.server.fastmcp import FastMCP
# + from fastmcp import FastMCP

from fastmcp import FastMCP

mcp = FastMCP("whatsapp")
