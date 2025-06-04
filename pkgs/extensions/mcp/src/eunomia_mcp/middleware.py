import json
import logging
from typing import Any, Optional

from eunomia_core import schemas
from eunomia_sdk_python import EunomiaClient
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from eunomia_mcp.schemas import JsonRpcError, JsonRpcErrorResponse, JsonRpcRequest

logger = logging.getLogger(__name__)


class EunomiaMcpMiddleware(BaseHTTPMiddleware):
    """
    Eunomia authorization middleware for MCP servers.

    This middleware intercepts JSON-RPC 2.0 requests and validates them against
    Eunomia policies before allowing them to proceed to the MCP server.
    """

    def __init__(
        self,
        app,
        eunomia_client: Optional[EunomiaClient] = None,
        enable_audit_logging: bool = True,
        bypass_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self._eunomia_client = eunomia_client or EunomiaClient()
        self._enable_audit_logging = enable_audit_logging
        self._bypass_paths = bypass_paths or ["/health", "/status", "/docs"]

    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch method."""

        # Skip authorization for bypass paths
        if any(request.url.path.startswith(path) for path in self._bypass_paths):
            return await call_next(request)

        # Only process JSON-RPC requests
        if not self._is_jsonrpc_request(request):
            return await call_next(request)

        # Parse and validate JSON-RPC request
        try:
            body = await request.body()
            raw_data = json.loads(body.decode())
            jsonrpc_request = JsonRpcRequest(**raw_data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return JsonRpcErrorResponse(
                error=JsonRpcError(code=-32700, message="Parse error", data=str(e))
            ).as_starlette_json_response()
        except ValidationError as e:
            return JsonRpcErrorResponse(
                error=JsonRpcError(
                    code=-32600,
                    message="Invalid Request",
                    data=f"Invalid JSON-RPC 2.0 format: {str(e)}",
                )
            ).as_starlette_json_response()

        # Perform authorization check
        auth_result = await self._authorize_request(jsonrpc_request, request)

        if not auth_result.allowed:
            if self._enable_audit_logging:
                self._log_violation(request, jsonrpc_request, auth_result.reason)
            return JsonRpcErrorResponse(
                error=JsonRpcError(
                    code=-32603, message="Unauthorized", data=auth_result.reason
                ),
                id=jsonrpc_request.id,
            ).as_starlette_json_response()

        # Log successful authorization
        if self._enable_audit_logging:
            self._log_authorized_request(request, jsonrpc_request)

        # Reconstruct request body for downstream processing
        request._body = body

        return await call_next(request)

    def _is_jsonrpc_request(self, request: Request) -> bool:
        """Check if request is a JSON-RPC request."""
        content_type = request.headers.get("content-type", "")
        return request.method == "POST" and (
            "application/json" in content_type.lower()
            or "application/json-rpc" in content_type.lower()
        )

    async def _authorize_request(
        self, jsonrpc_request: JsonRpcRequest, request: Request
    ) -> schemas.CheckResponse:
        """Perform authorization check using Eunomia."""
        try:
            # Extract principal information
            principal_info = self._extract_principal_info(request)

            # Map MCP method to resource/action
            params = jsonrpc_request.get_dict_params()
            resource_info = self._map_method_to_resource(jsonrpc_request.method, params)

            return self._eunomia_client.check(
                principal_uri=principal_info.get("uri"),
                principal_attributes=principal_info.get("attributes", {}),
                resource_uri=resource_info.get("uri"),
                resource_attributes=resource_info.get("attributes", {}),
                action=resource_info.get("action", "access"),
            )

        except Exception as e:
            logger.error(f"Authorization check failed: {e}")
            return schemas.CheckResponse(
                allowed=False, reason=f"Authorization system error: {str(e)}"
            )

    def _extract_principal_info(self, request: Request) -> dict[str, Any]:
        """Extract principal information from request."""
        principal_info = {"attributes": {}}

        # Extract from custom headers
        agent_id = request.headers.get("X-Agent-ID")
        user_id = request.headers.get("X-User-ID")
        api_key = request.headers.get("Authorization")

        if agent_id:
            principal_info["uri"] = f"agent:{agent_id}"
            principal_info["attributes"]["agent_id"] = agent_id

        if user_id:
            principal_info["attributes"]["user_id"] = user_id

        if api_key:
            principal_info["attributes"]["api_key"] = api_key.replace("Bearer ", "")

        # Default fallback
        if not principal_info.get("uri"):
            principal_info["uri"] = "agent:unknown"
            principal_info["attributes"]["type"] = "unknown_agent"

        return principal_info

    def _map_method_to_resource(
        self, method: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Map MCP JSON-RPC method to Eunomia resource/action."""
        default_attributes = {"mcp_method": method, "type": "mcp_resource"}

        tool_name = params.get("name") if method == "tools/call" else ""
        resource_uri = params.get("uri") if method == "resources/read" else ""
        prompt_name = params.get("name") if method == "prompts/get" else ""

        methods_mapping = {
            "tools/list": {
                "action": "access",
                "uri": "mcp:tools",
                "attributes": {"resource_type": "tools"},
            },
            "tools/call": {
                "action": "execute",
                "uri": f"mcp:tools:{tool_name}",
                "attributes": {
                    "resource_type": "tools",
                    "tool_name": tool_name,
                },
            },
            "resources/list": {
                "action": "access",
                "uri": "mcp:resources",
                "attributes": {"resource_type": "resources"},
            },
            "resources/read": {
                "action": "read",
                "uri": f"mcp:resources:{resource_uri}",
                "attributes": {
                    "resource_type": "resources",
                    "resource_uri": resource_uri,
                },
            },
            "prompts/list": {
                "action": "access",
                "uri": "mcp:prompts",
                "attributes": {"resource_type": "prompts"},
            },
            "prompts/get": {
                "action": "read",
                "uri": f"mcp:prompts:{prompt_name}",
                "attributes": {
                    "resource_type": "prompts",
                    "prompt_name": prompt_name,
                },
            },
            "other": {
                "action": "access",
                "uri": f"mcp:method:{method}",
                "attributes": {"resource_type": "other"},
            },
        }

        resource_info = methods_mapping.get(method, methods_mapping["other"])
        resource_info["attributes"].update(default_attributes)
        return resource_info

    def _log_violation(
        self, request: Request, jsonrpc_request: JsonRpcRequest, reason: str
    ):
        """Log authorization violations."""
        logger.warning(
            f"Authorization violation: {reason} | "
            f"Method: {jsonrpc_request.method} | "
            f"Client: {request.client.host if request.client else 'unknown'} | "
            f"User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )

    def _log_authorized_request(
        self, request: Request, jsonrpc_request: JsonRpcRequest
    ):
        """Log authorized requests."""
        logger.info(
            f"Authorized MCP request: {jsonrpc_request.method} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
