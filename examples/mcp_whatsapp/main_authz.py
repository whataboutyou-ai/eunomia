from eunomia_mcp import create_eunomia_middleware

from .main import mcp

middleware = create_eunomia_middleware()
app = mcp.add_middleware(middleware)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8088)
