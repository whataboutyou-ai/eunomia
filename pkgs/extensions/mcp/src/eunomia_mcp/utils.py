from typing import Optional

from eunomia_sdk import EunomiaClient
from fastmcp.server.middleware import Middleware

from eunomia.config import settings
from eunomia.server import EunomiaServer
from eunomia_mcp.bridge import EunomiaMode
from eunomia_mcp.middleware import EunomiaMcpMiddleware


def create_eunomia_middleware(
    use_remote_eunomia: bool = False,
    eunomia_endpoint: Optional[str] = None,
    enable_audit_logging: bool = True,
) -> Middleware:
    """
    Create Eunomia authorization middleware for FastMCP servers.

    Parameters
    ----------
    use_remote_eunomia : bool, optional
        Whether to use a remote Eunomia server (defaults to False)
    eunomia_endpoint : str, optional
        Eunomia server endpoint when using a remote server (defaults to http://localhost:8421)
    enable_audit_logging : bool, optional
        Whether to enable audit logging

    Returns
    -------
    Middleware
        FastMCP Middleware instance
    """
    client, server = None, None
    if use_remote_eunomia:
        mode = EunomiaMode.CLIENT
        client = EunomiaClient(endpoint=eunomia_endpoint)
    else:
        mode = EunomiaMode.SERVER
        # enforce no database persistence
        settings.ENGINE_SQL_DATABASE = False
        server = EunomiaServer()

    return EunomiaMcpMiddleware(
        mode=mode,
        eunomia_client=client,
        eunomia_server=server,
        enable_audit_logging=enable_audit_logging,
    )
