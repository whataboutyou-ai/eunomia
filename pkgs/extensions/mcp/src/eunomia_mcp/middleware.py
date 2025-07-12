import logging
from typing import Optional

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

from eunomia_mcp.schemas import McpAttributes

logger = logging.getLogger(__name__)


class EunomiaMcpMiddleware(Middleware):
    """
    Eunomia authorization middleware for MCP servers.
    """

    def __init__(
        self,
        eunomia_client: Optional[EunomiaClient] = None,
        enable_audit_logging: bool = True,
    ):
        self._eunomia_client = eunomia_client or EunomiaClient()
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

    def _authorize_call(
        self, context: MiddlewareContext, component: FastMCPComponent
    ) -> None:
        if not component.enabled:
            raise ToolError(f"Access denied: {component.name} is disabled")

        principal = self._extract_principal()
        action = context.method.split("/")[1]
        resource = self._extract_resource(context, component)

        result = self._eunomia_client.check(
            principal_uri=principal.uri,
            principal_attributes=principal.attributes,
            resource_uri=resource.uri,
            resource_attributes=resource.attributes,
            action=action,
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

    def _authorize_list(
        self, context: MiddlewareContext, components: list[FastMCPComponent]
    ) -> list[FastMCPComponent]:
        if components:
            principal = self._extract_principal()
            action = context.method.split("/")[1]

            # Construct requests for bulk check
            resources = [self._extract_resource(context, c) for c in components]

            # Perform all checks in bulk
            results = self._eunomia_client.bulk_check(
                [
                    schemas.CheckRequest(principal=principal, resource=r, action=action)
                    for r in resources
                ]
            )

            # Disable components based on its authorization result
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
        self._authorize_call(context, tool)
        result = await call_next(context)
        return result

    async def on_read_resource(
        self,
        context: MiddlewareContext[types.ReadResourceRequestParams],
        call_next: CallNext[types.ReadResourceRequestParams, types.ReadResourceResult],
    ) -> types.ReadResourceResult:
        resource = await context.fastmcp_context.fastmcp.get_resource(
            context.message.uri
        )
        self._authorize_call(context, resource)
        return await call_next(context)

    async def on_get_prompt(
        self,
        context: MiddlewareContext[types.GetPromptRequestParams],
        call_next: CallNext[types.GetPromptRequestParams, types.GetPromptResult],
    ) -> types.GetPromptResult:
        prompt = await context.fastmcp_context.fastmcp.get_prompt(context.message.name)
        self._authorize_call(context, prompt)
        return await call_next(context)

    async def on_list_tools(
        self,
        context: MiddlewareContext[types.ListToolsRequest],
        call_next: CallNext[types.ListToolsRequest, list[Tool]],
    ) -> list[Tool]:
        result = await call_next(context)
        return self._authorize_list(context, result)

    async def on_list_resources(
        self,
        context: MiddlewareContext[types.ListResourcesRequest],
        call_next: CallNext[types.ListResourcesRequest, list[Resource]],
    ) -> list[Resource]:
        result = await call_next(context)
        return self._authorize_list(context, result)

    async def on_list_prompts(
        self,
        context: MiddlewareContext[types.ListPromptsRequest],
        call_next: CallNext[types.ListPromptsRequest, list[Prompt]],
    ) -> list[Prompt]:
        result = await call_next(context)
        return self._authorize_list(context, result)
