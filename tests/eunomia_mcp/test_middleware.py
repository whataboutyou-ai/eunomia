import json
from unittest.mock import Mock, patch

import pytest
from eunomia_core.schemas import CheckResponse
from eunomia_mcp.middleware import EunomiaMcpMiddleware
from eunomia_mcp.schemas import JsonRpcError, JsonRpcErrorResponse, JsonRpcRequest
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient


class TestEunomiaAuthMiddleware:
    """Test suite for EunomiaMcpMiddleware."""

    @pytest.fixture
    def mock_eunomia_client(self):
        """Mock Eunomia client."""
        client = Mock()
        client.check = Mock(
            return_value=CheckResponse(allowed=True, reason="Authorized")
        )
        return client

    @pytest.fixture
    def middleware(self, mock_eunomia_client):
        """Create middleware instance."""
        app = Starlette()
        return EunomiaMcpMiddleware(
            app=app,
            eunomia_client=mock_eunomia_client,
            enable_audit_logging=True,
        )

    @pytest.fixture
    def test_app(self, middleware):
        """Create test application with middleware."""

        async def mcp_endpoint(request):
            return JSONResponse({"result": "success"})

        async def health_endpoint(request):
            return JSONResponse({"status": "ok"})

        routes = [
            Route("/mcp", endpoint=mcp_endpoint, methods=["POST"]),
            Route("/health", endpoint=health_endpoint, methods=["GET"]),
        ]
        app = Starlette(routes=routes)

        app.add_middleware(
            EunomiaMcpMiddleware, eunomia_client=middleware._eunomia_client
        )
        return app

    def test_bypass_paths(self, test_app):
        """Test that bypass paths skip authorization."""
        client = TestClient(test_app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_non_jsonrpc_requests_pass_through(self, test_app):
        """Test that non-JSON-RPC requests pass through."""
        client = TestClient(test_app)
        response = client.get("/mcp")
        # Should get method not allowed, not authorization error
        assert response.status_code == 405

    def test_invalid_json_returns_parse_error(self, test_app):
        """Test that invalid JSON returns parse error."""
        client = TestClient(test_app)
        response = client.post(
            "/mcp", content="invalid json", headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == -32700
        assert "Parse error" in data["error"]["message"]

    def test_invalid_jsonrpc_format(self, test_app):
        """Test that invalid JSON-RPC format is rejected."""
        client = TestClient(test_app)
        response = client.post(
            "/mcp",
            json={"invalid": "format"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == -32600
        assert "Invalid Request" in data["error"]["message"]

    def test_missing_jsonrpc_version(self, test_app):
        """Test that missing jsonrpc version is rejected."""
        client = TestClient(test_app)
        response = client.post(
            "/mcp",
            json={"method": "test_method", "id": 1},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == -32600
        assert "Invalid Request" in data["error"]["message"]

    def test_wrong_jsonrpc_version(self, test_app):
        """Test that wrong JSON-RPC version is rejected."""
        client = TestClient(test_app)
        response = client.post(
            "/mcp",
            json={"jsonrpc": "1.0", "method": "test_method", "id": 1},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == -32600
        assert "Invalid Request" in data["error"]["message"]

    @patch("eunomia_mcp.middleware.EunomiaMcpMiddleware._authorize_request")
    def test_authorization_success(self, mock_authorize, test_app):
        """Test successful authorization."""
        mock_authorize.return_value = CheckResponse(allowed=True, reason="Authorized")

        client = TestClient(test_app)
        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
            headers={"Content-Type": "application/json", "X-Agent-ID": "test-agent"},
        )
        assert response.status_code == 200
        assert response.json() == {"result": "success"}

    @patch("eunomia_mcp.middleware.EunomiaMcpMiddleware._authorize_request")
    def test_authorization_failure(self, mock_authorize, test_app):
        """Test authorization failure."""
        mock_authorize.return_value = CheckResponse(
            allowed=False, reason="Access denied"
        )

        client = TestClient(test_app)
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "restricted_tool"},
                "id": 1,
            },
            headers={"Content-Type": "application/json", "X-Agent-ID": "test-agent"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == -32603
        assert "Unauthorized" in data["error"]["message"]
        assert data["id"] == 1

    def test_extract_principal_info_with_headers(self, middleware):
        """Test principal extraction from headers."""
        request = Mock()
        request.headers = {
            "X-Agent-ID": "claude",
            "X-User-ID": "user123",
            "Authorization": "Bearer api-key-123",
        }

        principal_uri, principal_attributes = middleware._extract_principal_info(
            request
        )

        assert principal_uri == "agent:claude"
        assert principal_attributes["agent_id"] == "claude"
        assert principal_attributes["user_id"] == "user123"
        assert principal_attributes["api_key"] == "api-key-123"

    def test_extract_principal_info_fallback(self, middleware):
        """Test principal extraction fallback."""
        request = Mock()
        request.headers = {}

        principal_uri, principal_attributes = middleware._extract_principal_info(
            request
        )

        assert principal_uri == "agent:unknown"
        assert principal_attributes["type"] == "unknown_agent"

    def test_map_tools_method(self, middleware):
        """Test mapping of tools methods."""
        # Test tools/list
        action, uri, attributes = middleware._map_method_to_action_and_resource(
            "tools/list", {}
        )
        assert uri == "mcp:tools"
        assert action == "access"
        assert attributes["resource_type"] == "tools"

        # Test tools/call
        params = {"name": "read_file", "arguments": {"path": "test.txt"}}
        action, uri, attributes = middleware._map_method_to_action_and_resource(
            "tools/call", params
        )
        assert uri == "mcp:tools:read_file"
        assert action == "execute"
        assert attributes["tool_name"] == "read_file"
        assert attributes["arguments"] == {"path": "test.txt"}

    def test_map_resources_method(self, middleware):
        """Test mapping of resources methods."""
        # Test resources/list
        action, uri, attributes = middleware._map_method_to_action_and_resource(
            "resources/list", {}
        )
        assert uri == "mcp:resources"
        assert action == "access"

        # Test resources/read
        params = {"uri": "file://test.txt"}
        action, uri, attributes = middleware._map_method_to_action_and_resource(
            "resources/read", params
        )
        assert uri == "mcp:resources:file://test.txt"
        assert action == "read"
        assert attributes["resource_uri"] == "file://test.txt"

    def test_map_prompts_method(self, middleware):
        """Test mapping of prompts methods."""
        # Test prompts/list
        action, uri, attributes = middleware._map_method_to_action_and_resource(
            "prompts/list", {}
        )
        assert uri == "mcp:prompts"
        assert action == "access"

        # Test prompts/get
        params = {"name": "test_prompt"}
        action, uri, attributes = middleware._map_method_to_action_and_resource(
            "prompts/get", params
        )
        assert uri == "mcp:prompts:test_prompt"
        assert action == "read"
        assert attributes["prompt_name"] == "test_prompt"

    def test_map_generic_method(self, middleware):
        """Test mapping of generic methods."""
        action, uri, attributes = middleware._map_method_to_action_and_resource(
            "custom/method", {}
        )
        assert uri == "mcp:method:custom/method"
        assert action == "access"

    def test_is_jsonrpc_request(self, middleware):
        """Test JSON-RPC request detection."""
        # Valid JSON-RPC request
        request = Mock()
        request.method = "POST"
        request.headers = {"content-type": "application/json"}
        assert middleware._is_jsonrpc_request(request) is True

        # Invalid method
        request.method = "GET"
        assert middleware._is_jsonrpc_request(request) is False

        # Invalid content type
        request.method = "POST"
        request.headers = {"content-type": "text/plain"}
        assert middleware._is_jsonrpc_request(request) is False

    def test_jsonrpc_schema_validation(self):
        """Test JSON-RPC schema validation."""
        # Valid JSON-RPC
        valid_data = {"jsonrpc": "2.0", "method": "test_method", "id": 1}
        request = JsonRpcRequest(**valid_data)
        assert request.method == "test_method"
        assert request.id == 1

        # Valid JSON-RPC with params
        valid_data_with_params = {
            "jsonrpc": "2.0",
            "method": "test_method",
            "params": {"arg1": "value1"},
            "id": 1,
        }
        request = JsonRpcRequest(**valid_data_with_params)
        assert request.params == {"arg1": "value1"}

        # Valid JSON-RPC notification (no id)
        notification_data = {"jsonrpc": "2.0", "method": "test_method"}
        request = JsonRpcRequest(**notification_data)
        assert request.id is None

        # Wrong jsonrpc version
        invalid_version = {"jsonrpc": "1.0", "method": "test_method", "id": 1}
        with pytest.raises(ValidationError):
            request = JsonRpcRequest(**invalid_version)

    def test_create_jsonrpc_error(self, middleware):
        """Test JSON-RPC error response creation."""
        response = JsonRpcErrorResponse(
            error=JsonRpcError(
                code=-32603, message="Test error", data="Additional data"
            ),
            id=123,
        ).as_starlette_json_response()

        assert isinstance(response, JSONResponse)
        content = json.loads(response.body.decode())

        assert content["jsonrpc"] == "2.0"
        assert content["error"]["code"] == -32603
        assert content["error"]["message"] == "Test error"
        assert content["error"]["data"] == "Additional data"
        assert content["id"] == 123

    @pytest.mark.asyncio
    async def test_params_handling_with_list(self, middleware):
        """Test that list params are converted to empty dict for mapping."""
        # Create a mock JsonRpcRequest with list params
        jsonrpc_request = JsonRpcRequest(
            jsonrpc="2.0", method="test_method", params=["param1", "param2"], id=1
        )

        request = Mock()
        request.headers = {"X-Agent-ID": "test-agent"}

        # This should not raise an error and should handle list params gracefully
        result = await middleware._authorize_request(jsonrpc_request, request)
        # The actual result depends on the mocked client, but we're testing that no exception is raised
        assert result is not None
