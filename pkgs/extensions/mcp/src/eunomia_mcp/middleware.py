import logging

from eunomia_core import schemas
from eunomia_sdk import EunomiaClient
from fastmcp.exceptions import ToolError
from fastmcp.prompts.prompt import Prompt
from fastmcp.resources.resource import Resource
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import Tool
from fastmcp.utilities.components import FastMCPComponent
from mcp import types

from eunomia.server import EunomiaServer
from eunomia_mcp.bridge import EunomiaBridge, EunomiaMode
from eunomia_mcp.schemas import McpAttributes

logger = logging.getLogger(__name__)


class EunomiaMcpMiddleware(Middleware):
    """
    Eunomia authorization middleware for MCP servers.
    """

    def __init__(
        self,
        mode: EunomiaMode = EunomiaMode.SERVER,
        eunomia_client: EunomiaClient | None = None,
        eunomia_server: EunomiaServer | None = None,
        enable_audit_logging: bool = True,
    ):
        self._eunomia = EunomiaBridge(mode, eunomia_client, eunomia_server)
        self._enable_audit_logging = enable_audit_logging

    def _extract_principal(self) -> schemas.PrincipalCheck:
        headers = get_http_headers()

        agent_id = headers.get("x-agent-id", "unknown")
        user_id = headers.get("x-user-id", "unknown")
        user_agent = headers.get("user-agent", "undefined")
        api_key = headers.get("authorization")

        uri = f"agent:{agent_id}"
        attributes = {
            "agent_id": agent_id,
            "user_id": user_id,
            "user_agent": user_agent,
        }
        if api_key:
            attributes["api_key"] = api_key.replace("Bearer ", "")

        return schemas.PrincipalCheck(uri=uri, attributes=attributes)

    def _extract_resource(
        self, context: MiddlewareContext, component: FastMCPComponent
    ) -> schemas.ResourceCheck:
        component_type = context.method.split("/")[0]

        uri = f"mcp:{component_type}:{component.name}"
        mcp_attributes = McpAttributes(
            method=context.method,
            component_type=component_type,
            name=component.name,
            uri=uri,
            arguments=getattr(context.message, "arguments", None),
        )

        return schemas.ResourceCheck(
            uri=uri, attributes=mcp_attributes.model_dump(exclude_none=True)
        )

    async def _authorize_execution(
        self, context: MiddlewareContext, component: FastMCPComponent
    ) -> None:
        if not component.enabled:
            raise ToolError(f"Access denied: {component.name} is disabled")

        action = "execute"
        principal = self._extract_principal()
        resource = self._extract_resource(context, component)

        result = await self._eunomia.check(
            schemas.CheckRequest(principal=principal, resource=resource, action=action)
        )

        if self._enable_audit_logging:
            self._log_authorization(
                principal,
                resource,
                context.method,
                result.reason,
                is_violation=(not result.allowed),
            )

        if not result.allowed:
            raise ToolError(f"Access denied: {result.reason}")

    async def _authorize_listing(
        self, context: MiddlewareContext, components: list[FastMCPComponent]
    ) -> list[FastMCPComponent]:
        if components:
            action = "list"
            principal = self._extract_principal()

            # Construct requests for bulk check
            resources = [self._extract_resource(context, c) for c in components]

            # Perform all checks in bulk
            results = await self._eunomia.bulk_check(
                [
                    schemas.CheckRequest(principal=principal, resource=r, action=action)
                    for r in resources
                ]
            )

            # Filter components based on authorization results
            filtered_components = []
            for result, component, resource in zip(results, components, resources):
                if result.allowed:
                    filtered_components.append(component)

                if self._enable_audit_logging:
                    self._log_authorization(
                        principal,
                        resource,
                        context.method,
                        result.reason,
                        is_violation=(not result.allowed),
                    )

            return filtered_components
        return []

    def _log_authorization(
        self,
        principal: schemas.PrincipalCheck,
        resource: schemas.ResourceCheck,
        method: str,
        reason: str,
        is_violation: bool,
    ):
        info = (
            f"MCP method: {method} | "
            f"MCP uri: {resource.uri} | "
            f"User-Agent: {principal.attributes.get('user_agent')}"
        )

        if is_violation:
            logger.warning(f"Authorization violation: {reason} | " + info)
        else:
            logger.info(f"Authorized request: {reason} | " + info)

    async def on_call_tool(
        self,
        context: MiddlewareContext[types.CallToolRequestParams],
        call_next: CallNext[types.CallToolRequestParams, types.CallToolResult],
    ) -> types.CallToolResult:
        tool = await context.fastmcp_context.fastmcp.get_tool(context.message.name)
        await self._authorize_execution(context, tool)
        return await call_next(context)

    async def on_read_resource(
        self,
        context: MiddlewareContext[types.ReadResourceRequestParams],
        call_next: CallNext[types.ReadResourceRequestParams, types.ReadResourceResult],
    ) -> types.ReadResourceResult:
        resource = await context.fastmcp_context.fastmcp.get_resource(
            context.message.uri
        )
        await self._authorize_execution(context, resource)
        return await call_next(context)

    async def on_get_prompt(
        self,
        context: MiddlewareContext[types.GetPromptRequestParams],
        call_next: CallNext[types.GetPromptRequestParams, types.GetPromptResult],
    ) -> types.GetPromptResult:
        prompt = await context.fastmcp_context.fastmcp.get_prompt(context.message.name)
        await self._authorize_execution(context, prompt)
        return await call_next(context)

    async def on_list_tools(
        self,
        context: MiddlewareContext[types.ListToolsRequest],
        call_next: CallNext[types.ListToolsRequest, list[Tool]],
    ) -> list[Tool]:
        tools = await call_next(context)
        return await self._authorize_listing(context, tools)

    async def on_list_resources(
        self,
        context: MiddlewareContext[types.ListResourcesRequest],
        call_next: CallNext[types.ListResourcesRequest, list[Resource]],
    ) -> list[Resource]:
        resources = await call_next(context)
        return await self._authorize_listing(context, resources)

    async def on_list_prompts(
        self,
        context: MiddlewareContext[types.ListPromptsRequest],
        call_next: CallNext[types.ListPromptsRequest, list[Prompt]],
    ) -> list[Prompt]:
        prompts = await call_next(context)
        return await self._authorize_listing(context, prompts)
