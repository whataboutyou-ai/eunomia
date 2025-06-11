import fnmatch
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
        bypass_methods: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self._eunomia_client = eunomia_client or EunomiaClient()
        self._enable_audit_logging = enable_audit_logging
        self._bypass_methods = bypass_methods or [
            "initialize",
            "ping",
            "notifications/*",
        ]

    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch method."""

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

        # Skip authorization for bypass methods
        if any(
            fnmatch.fnmatch(jsonrpc_request.method, pattern)
            for pattern in self._bypass_methods
        ):
            return await call_next(request)

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
            principal_uri, principal_attributes = self._extract_principal_info(request)

            # Map MCP method to action and resource
            params = jsonrpc_request.get_dict_params()
            action, resource_uri, resource_attributes = (
                self._map_method_to_action_and_resource(jsonrpc_request.method, params)
            )

            return self._eunomia_client.check(
                principal_uri=principal_uri,
                principal_attributes=principal_attributes,
                resource_uri=resource_uri,
                resource_attributes=resource_attributes,
                action=action,
            )

        except Exception as e:
            logger.error(f"Authorization check failed: {e}")
            return schemas.CheckResponse(
                allowed=False, reason=f"Authorization system error: {str(e)}"
            )

    def _extract_principal_info(self, request: Request) -> tuple[str, dict[str, Any]]:
        """Extract principal information from request."""
        uri = None
        attributes = {}

        # Extract from custom headers
        agent_id = request.headers.get("X-Agent-ID")
        user_id = request.headers.get("X-User-ID")
        api_key = request.headers.get("Authorization")

        if agent_id:
            uri = f"agent:{agent_id}"
            attributes["agent_id"] = agent_id

        if user_id:
            attributes["user_id"] = user_id

        if api_key:
            attributes["api_key"] = api_key.replace("Bearer ", "")

        # Default fallback
        if not uri:
            uri = "agent:unknown"
            attributes["type"] = "unknown_agent"

        return uri, attributes

    def _map_method_to_action_and_resource(
        self, method: str, params: dict[str, Any]
    ) -> tuple[str, str, dict[str, Any]]:
        """Map MCP JSON-RPC method to Eunomia resource/action."""
        known_methods = [
            "tools/list",
            "prompts/list",
            "resources/list",
            "tools/call",
            "resources/read",
            "prompts/get",
        ]

        if method in known_methods:
            resource_type = method.split("/")[0]
            uri = f"mcp:{resource_type}"
        else:
            resource_type = "unknown"
            uri = f"mcp:method:{method}"

        action = "access"
        attributes = {
            "type": "mcp_resource",
            "mcp_method": method,
            "resource_type": resource_type,
            "arguments": params.get("arguments", {}),
        }

        if method == "tools/call":
            action = "execute"
            uri = uri + f":{params.get('name')}"
            attributes["tool_name"] = params.get("name")
        elif method == "resources/read":
            action = "read"
            uri = uri + f":{params.get('uri')}"
            attributes["resource_uri"] = params.get("uri")
        elif method == "prompts/get":
            action = "read"
            uri = uri + f":{params.get('name')}"
            attributes["prompt_name"] = params.get("name")

        return action, uri, attributes

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
