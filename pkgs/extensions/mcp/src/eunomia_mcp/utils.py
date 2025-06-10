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

    Parameters
    ----------
    eunomia_endpoint : str, optional
        Eunomia server endpoint (defaults to localhost:8000)
    eunomia_api_key : str, optional
        API key for Eunomia server (or set WAY_API_KEY env var)
    enable_audit_logging : bool, optional
        Whether to enable audit logging
    bypass_methods : list[str], optional
        List of methods to bypass authorization

    Returns
    -------
    Middleware
        Starlette Middleware instance ready for FastMCP
    """
    client = EunomiaClient(endpoint=eunomia_endpoint, api_key=eunomia_api_key)

    return Middleware(
        EunomiaMcpMiddleware,
        eunomia_client=client,
        enable_audit_logging=enable_audit_logging,
        bypass_methods=bypass_methods,
    )
