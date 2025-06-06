from typing import Optional

from eunomia_sdk_python import EunomiaClient
from starlette.middleware import Middleware

from eunomia_mcp.middleware import EunomiaMcpMiddleware


def create_eunomia_middleware(
    eunomia_endpoint: Optional[str] = None,
    eunomia_api_key: Optional[str] = None,
    enable_audit_logging: bool = True,
    bypass_methods: Optional[list[str]] = None,
) -> Middleware:
    """
    Create Eunomia authorization middleware for FastMCP servers.

    Args:
        eunomia_endpoint: Eunomia server endpoint (defaults to localhost:8000)
        eunomia_api_key: API key for Eunomia server (or set WAY_API_KEY env var)
        enable_audit_logging: Whether to enable audit logging
        bypass_methods: List of methods to bypass authorization

    Returns:
        Starlette Middleware instance ready for FastMCP

    Example:
        ```python
        from fastmcp import FastMCP
        from eunomia_mcp import create_eunomia_middleware

        # Create FastMCP server
        mcp = FastMCP("MyServer")

        # Add Eunomia middleware
        middleware = [create_eunomia_middleware()]

        # Create ASGI app with middleware
        app = mcp.http_app(middleware=middleware)
        ```
    """
    client = EunomiaClient(endpoint=eunomia_endpoint, api_key=eunomia_api_key)

    return Middleware(
        EunomiaMcpMiddleware,
        eunomia_client=client,
        enable_audit_logging=enable_audit_logging,
        bypass_methods=bypass_methods,
    )
