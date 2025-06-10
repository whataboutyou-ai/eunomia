from eunomia_mcp import create_eunomia_middleware

from .main import mcp

middleware = [create_eunomia_middleware()]
app = mcp.http_app(middleware=middleware)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8088)
