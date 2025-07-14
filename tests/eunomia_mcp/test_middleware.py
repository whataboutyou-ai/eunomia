from unittest.mock import AsyncMock, Mock, patch

import pytest
from eunomia_core.schemas import CheckResponse
from eunomia_mcp.middleware import EunomiaMcpMiddleware
from fastmcp.exceptions import ToolError
from fastmcp.prompts.prompt import Prompt
from fastmcp.resources.resource import Resource
from fastmcp.server.middleware import MiddlewareContext
from fastmcp.tools.tool import Tool
from mcp import types


class TestEunomiaMcpMiddleware:
    """Test suite for EunomiaMcpMiddleware."""

    @pytest.fixture
    def mock_eunomia_client(self):
        """Mock Eunomia client."""
        client = Mock()
        client.check = Mock(
            return_value=CheckResponse(allowed=True, reason="Authorized")
        )
        client.bulk_check = Mock(
            return_value=[CheckResponse(allowed=True, reason="Authorized")]
        )
        return client

    @pytest.fixture
    def middleware(self, mock_eunomia_client):
        """Create middleware instance."""
        return EunomiaMcpMiddleware(
            eunomia_client=mock_eunomia_client,
            enable_audit_logging=True,
        )

    @pytest.fixture
    def mock_tool(self):
        """Mock FastMCP tool."""
        tool = Mock(spec=Tool)
        tool.name = "test_tool"
        tool.enabled = True
        return tool

    @pytest.fixture
    def mock_resource(self):
        """Mock FastMCP resource."""
        resource = Mock(spec=Resource)
        resource.name = "test_resource"
        resource.enabled = True
        return resource

    @pytest.fixture
    def mock_prompt(self):
        """Mock FastMCP prompt."""
        prompt = Mock(spec=Prompt)
        prompt.name = "test_prompt"
        prompt.enabled = True
        return prompt

    @pytest.fixture
    def mock_context(self):
        """Mock MiddlewareContext."""
        context = Mock(spec=MiddlewareContext)
        context.method = "tools/call"
        context.message = Mock()
        context.message.name = "test_tool"
        # Configure mock to return specific values for getattr calls
        context.message.configure_mock(arguments={"arg1": "value1"}, uri=None)
        context.fastmcp_context = Mock()
        context.fastmcp_context.fastmcp = Mock()
        return context

    @patch("eunomia_mcp.middleware.get_http_headers")
    def test_extract_principal_with_headers(self, mock_get_headers, middleware):
        """Test principal extraction from headers."""
        mock_get_headers.return_value = {
            "x-agent-id": "claude",
            "x-user-id": "user123",
            "user-agent": "test-agent",
            "authorization": "Bearer api-key-123",
        }

        principal = middleware._extract_principal()

        assert principal.uri == "agent:claude"
        assert principal.attributes["agent_id"] == "claude"
        assert principal.attributes["user_id"] == "user123"
        assert principal.attributes["user_agent"] == "test-agent"
        assert principal.attributes["api_key"] == "api-key-123"

    @patch("eunomia_mcp.middleware.get_http_headers")
    def test_extract_principal_fallback(self, mock_get_headers, middleware):
        """Test principal extraction fallback."""
        mock_get_headers.return_value = {}

        principal = middleware._extract_principal()

        assert principal.uri == "agent:unknown"
        assert principal.attributes["agent_id"] == "unknown"
        assert principal.attributes["user_id"] == "unknown"
        assert principal.attributes["user_agent"] == "undefined"

    def test_extract_resource_for_tool(self, middleware, mock_context, mock_tool):
        """Test resource extraction for tool component."""
        mock_context.method = "tools/call"
        # Configure mock to return specific values for getattr calls
        mock_context.message.configure_mock(uri=None, arguments={"arg1": "value1"})

        resource = middleware._extract_resource(mock_context, mock_tool)

        assert resource.uri == "mcp:tools:test_tool"
        assert resource.attributes["method"] == "tools/call"
        assert resource.attributes["component_type"] == "tools"
        assert resource.attributes["name"] == "test_tool"
        assert resource.attributes["arguments"] == {"arg1": "value1"}

    def test_extract_resource_for_resource(
        self, middleware, mock_context, mock_resource
    ):
        """Test resource extraction for resource component."""
        mock_context.method = "resources/read"
        # Configure mock to return specific values for getattr calls
        mock_context.message.configure_mock(arguments=None)

        resource = middleware._extract_resource(mock_context, mock_resource)

        assert resource.uri == "mcp:resources:test_resource"
        assert resource.attributes["method"] == "resources/read"
        assert resource.attributes["component_type"] == "resources"
        assert resource.attributes["name"] == "test_resource"
        assert resource.attributes["uri"] == "mcp:resources:test_resource"

    def test_extract_resource_for_prompt(self, middleware, mock_context, mock_prompt):
        """Test resource extraction for prompt component."""
        mock_context.method = "prompts/get"
        # Configure mock to return specific values for getattr calls
        mock_context.message.configure_mock(uri=None, arguments=None)

        resource = middleware._extract_resource(mock_context, mock_prompt)

        assert resource.uri == "mcp:prompts:test_prompt"
        assert resource.attributes["method"] == "prompts/get"
        assert resource.attributes["component_type"] == "prompts"
        assert resource.attributes["name"] == "test_prompt"

    @patch("eunomia_mcp.middleware.get_http_headers")
    def test_authorize_call_success(
        self, mock_get_headers, middleware, mock_context, mock_tool
    ):
        """Test successful authorization for component call."""
        mock_get_headers.return_value = {"x-agent-id": "test-agent"}
        middleware._eunomia_client.check.return_value = CheckResponse(
            allowed=True, reason="Authorized"
        )

        # Should not raise any exception
        middleware._authorize_call(mock_context, mock_tool)

        middleware._eunomia_client.check.assert_called_once()

    @patch("eunomia_mcp.middleware.get_http_headers")
    def test_authorize_call_failure(
        self, mock_get_headers, middleware, mock_context, mock_tool
    ):
        """Test authorization failure for component call."""
        mock_get_headers.return_value = {"x-agent-id": "test-agent"}
        middleware._eunomia_client.check.return_value = CheckResponse(
            allowed=False, reason="Access denied"
        )

        with pytest.raises(ToolError, match="Access denied"):
            middleware._authorize_call(mock_context, mock_tool)

    def test_authorize_call_disabled_component(
        self, middleware, mock_context, mock_tool
    ):
        """Test authorization failure for disabled component."""
        mock_tool.enabled = False

        with pytest.raises(ToolError, match="Access denied: test_tool is disabled"):
            middleware._authorize_call(mock_context, mock_tool)

    @patch("eunomia_mcp.middleware.get_http_headers")
    def test_authorize_list_success(self, mock_get_headers, middleware, mock_context):
        """Test successful authorization for list operation."""
        mock_get_headers.return_value = {"x-agent-id": "test-agent"}
        mock_context.method = "tools/list"
        # Configure mock message for list operations
        mock_context.message.configure_mock(uri=None, arguments=None)

        tool1 = Mock(spec=Tool)
        tool1.name = "tool1"
        tool1.enabled = True
        tool2 = Mock(spec=Tool)
        tool2.name = "tool2"
        tool2.enabled = True

        components = [tool1, tool2]

        middleware._eunomia_client.bulk_check.return_value = [
            CheckResponse(allowed=True, reason="Authorized"),
            CheckResponse(allowed=True, reason="Authorized"),
        ]

        result = middleware._authorize_list(mock_context, components)

        assert len(result) == 2
        assert result == components
        middleware._eunomia_client.bulk_check.assert_called_once()

    @patch("eunomia_mcp.middleware.get_http_headers")
    def test_authorize_list_partial_filtering(
        self, mock_get_headers, middleware, mock_context
    ):
        """Test partial filtering in list operation."""
        mock_get_headers.return_value = {"x-agent-id": "test-agent"}
        mock_context.method = "tools/list"
        # Configure mock message for list operations
        mock_context.message.configure_mock(uri=None, arguments=None)

        tool1 = Mock(spec=Tool)
        tool1.name = "tool1"
        tool1.enabled = True
        tool2 = Mock(spec=Tool)
        tool2.name = "tool2"
        tool2.enabled = True

        components = [tool1, tool2]

        middleware._eunomia_client.bulk_check.return_value = [
            CheckResponse(allowed=True, reason="Authorized"),
            CheckResponse(allowed=False, reason="Access denied"),
        ]

        result = middleware._authorize_list(mock_context, components)

        assert len(result) == 1
        assert result[0] == tool1

    def test_authorize_list_empty_components(self, middleware, mock_context):
        """Test authorization with empty components list."""
        result = middleware._authorize_list(mock_context, [])
        assert result == []

    @patch("eunomia_mcp.middleware.logger")
    def test_log_authorization_success(self, mock_logger, middleware):
        """Test audit logging for successful authorization."""
        from eunomia_core.schemas import PrincipalCheck, ResourceCheck

        principal = PrincipalCheck(
            uri="agent:claude",
            attributes={"agent_id": "claude", "user_agent": "test-agent"},
        )
        resource = ResourceCheck(
            uri="mcp:tools:test_tool", attributes={"method": "tools/call"}
        )

        middleware._log_authorization(
            principal, resource, "tools/call", "Authorized", is_violation=False
        )

        mock_logger.info.assert_called_once()
        log_message = mock_logger.info.call_args[0][0]
        assert "Authorized request" in log_message
        assert "tools/call" in log_message

    @patch("eunomia_mcp.middleware.logger")
    def test_log_authorization_violation(self, mock_logger, middleware):
        """Test audit logging for authorization violation."""
        from eunomia_core.schemas import PrincipalCheck, ResourceCheck

        principal = PrincipalCheck(
            uri="agent:claude",
            attributes={"agent_id": "claude", "user_agent": "test-agent"},
        )
        resource = ResourceCheck(
            uri="mcp:tools:test_tool", attributes={"method": "tools/call"}
        )

        middleware._log_authorization(
            principal, resource, "tools/call", "Access denied", is_violation=True
        )

        mock_logger.warning.assert_called_once()
        log_message = mock_logger.warning.call_args[0][0]
        assert "Authorization violation" in log_message
        assert "tools/call" in log_message

    @pytest.mark.asyncio
    async def test_on_call_tool_success(self, middleware, mock_context, mock_tool):
        """Test on_call_tool method with successful authorization."""
        mock_context.fastmcp_context.fastmcp.get_tool = AsyncMock(
            return_value=mock_tool
        )

        call_next = AsyncMock(
            return_value=types.CallToolResult(
                content=[types.TextContent(type="text", text="success")]
            )
        )

        with patch.object(middleware, "_authorize_call") as mock_authorize:
            result = await middleware.on_call_tool(mock_context, call_next)

            mock_authorize.assert_called_once_with(mock_context, mock_tool)
            call_next.assert_called_once_with(mock_context)
            assert result.content[0].text == "success"

    @pytest.mark.asyncio
    async def test_on_call_tool_authorization_failure(
        self, middleware, mock_context, mock_tool
    ):
        """Test on_call_tool method with authorization failure."""
        mock_context.fastmcp_context.fastmcp.get_tool = AsyncMock(
            return_value=mock_tool
        )

        call_next = AsyncMock()

        with patch.object(
            middleware, "_authorize_call", side_effect=ToolError("Access denied")
        ):
            with pytest.raises(ToolError, match="Access denied"):
                await middleware.on_call_tool(mock_context, call_next)

            call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_read_resource_success(
        self, middleware, mock_context, mock_resource
    ):
        """Test on_read_resource method with successful authorization."""
        mock_context.fastmcp_context.fastmcp.get_resource = AsyncMock(
            return_value=mock_resource
        )

        call_next = AsyncMock(
            return_value=types.ReadResourceResult(
                contents=[
                    types.TextResourceContents(
                        uri="file://test.txt", mimeType="text/plain", text="content"
                    )
                ]
            )
        )

        with patch.object(middleware, "_authorize_call") as mock_authorize:
            result = await middleware.on_read_resource(mock_context, call_next)

            mock_authorize.assert_called_once_with(mock_context, mock_resource)
            call_next.assert_called_once_with(mock_context)
            assert result.contents[0].text == "content"

    @pytest.mark.asyncio
    async def test_on_get_prompt_success(self, middleware, mock_context, mock_prompt):
        """Test on_get_prompt method with successful authorization."""
        mock_context.fastmcp_context.fastmcp.get_prompt = AsyncMock(
            return_value=mock_prompt
        )

        call_next = AsyncMock(
            return_value=types.GetPromptResult(
                description="test prompt",
                messages=[
                    types.PromptMessage(
                        role="user", content=types.TextContent(type="text", text="test")
                    )
                ],
            )
        )

        with patch.object(middleware, "_authorize_call") as mock_authorize:
            result = await middleware.on_get_prompt(mock_context, call_next)

            mock_authorize.assert_called_once_with(mock_context, mock_prompt)
            call_next.assert_called_once_with(mock_context)
            assert result.description == "test prompt"

    @pytest.mark.asyncio
    async def test_on_list_tools_success(self, middleware, mock_context):
        """Test on_list_tools method with successful authorization."""
        tool1 = Mock(spec=Tool)
        tool1.name = "tool1"
        tool2 = Mock(spec=Tool)
        tool2.name = "tool2"

        tools = [tool1, tool2]
        call_next = AsyncMock(return_value=tools)

        with patch.object(
            middleware, "_authorize_list", return_value=tools
        ) as mock_authorize:
            result = await middleware.on_list_tools(mock_context, call_next)

            call_next.assert_called_once_with(mock_context)
            mock_authorize.assert_called_once_with(mock_context, tools)
            assert result == tools

    @pytest.mark.asyncio
    async def test_on_list_resources_success(self, middleware, mock_context):
        """Test on_list_resources method with successful authorization."""
        resource1 = Mock(spec=Resource)
        resource1.name = "resource1"
        resource2 = Mock(spec=Resource)
        resource2.name = "resource2"

        resources = [resource1, resource2]
        call_next = AsyncMock(return_value=resources)

        with patch.object(
            middleware, "_authorize_list", return_value=resources
        ) as mock_authorize:
            result = await middleware.on_list_resources(mock_context, call_next)

            call_next.assert_called_once_with(mock_context)
            mock_authorize.assert_called_once_with(mock_context, resources)
            assert result == resources

    @pytest.mark.asyncio
    async def test_on_list_prompts_success(self, middleware, mock_context):
        """Test on_list_prompts method with successful authorization."""
        prompt1 = Mock(spec=Prompt)
        prompt1.name = "prompt1"
        prompt2 = Mock(spec=Prompt)
        prompt2.name = "prompt2"

        prompts = [prompt1, prompt2]
        call_next = AsyncMock(return_value=prompts)

        with patch.object(
            middleware, "_authorize_list", return_value=prompts
        ) as mock_authorize:
            result = await middleware.on_list_prompts(mock_context, call_next)

            call_next.assert_called_once_with(mock_context)
            mock_authorize.assert_called_once_with(mock_context, prompts)
            assert result == prompts

    def test_middleware_initialization(self):
        """Test middleware initialization with different parameters."""
        # Test with default client
        middleware = EunomiaMcpMiddleware()
        assert middleware._eunomia_client is not None
        assert middleware._enable_audit_logging is True

        # Test with custom client
        custom_client = Mock()
        middleware = EunomiaMcpMiddleware(
            eunomia_client=custom_client, enable_audit_logging=False
        )
        assert middleware._eunomia_client is custom_client
        assert middleware._enable_audit_logging is False
