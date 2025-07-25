import asyncio
import importlib.util
import sys

from eunomia_core import enums, schemas
from eunomia_sdk import EunomiaClient
from fastmcp import FastMCP
from fastmcp.utilities.components import FastMCPComponent

from eunomia_mcp.utils import get_filepath, load_policy_config

DEFAULT_POLICY = schemas.Policy(
    version="1.0",
    name="mcp-default-policy",
    description="Default policy for a MCP server",
    default_effect=enums.PolicyEffect.DENY,
    rules=[
        schemas.Rule(
            name="unrestricted-access",
            description="All principals can list and execute tools, resources, and prompts",
            effect=enums.PolicyEffect.ALLOW,
            principal_conditions=[],
            resource_conditions=[],
            actions=["list", "execute"],
        ),
    ],
)

SAMPLE_SERVER_CODE = '''
from fastmcp import FastMCP
from eunomia_mcp import create_eunomia_middleware

# Create your FastMCP server
mcp = FastMCP("Secure MCP Server 🔒")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add middleware to your server
middleware = create_eunomia_middleware(policy_file="mcp_policies.json")
mcp.add_middleware(middleware)

if __name__ == "__main__":
    mcp.run()
'''


def push_policy_config(
    policy_file: str, overwrite: bool, client: EunomiaClient
) -> None:
    """
    Push a policy configuration file to Eunomia.

    Be careful, if overwrite is True, this action is destructive
    and will delete all existing policies.

    Args:
        policy_file: Path to policy configuration JSON file
        overwrite: Whether to overwrite existing policies
        client: the Eunomia client to use
    """
    new_policy = load_policy_config(policy_file)

    if overwrite:
        existing_policies = client.get_policies()
        for p in existing_policies:
            _ = client.delete_policy(p.name)

    _ = client.create_policy(new_policy)


def load_mcp_instance(mcp_path: str) -> FastMCP:
    """
    Load a FastMCP instance from a module path.

    Args:
        mcp_path: Path in format "module.path:variable_name", "path/to/file:variable_name" or "path/to/file.py:variable_name"

    Returns:
        FastMCP instance

    Raises:
        ValueError: If path format is invalid or instance is not found
        ImportError: If module cannot be imported
        TypeError: If the loaded object is not a FastMCP instance
    """
    if ":" not in mcp_path:
        raise ValueError(
            f"Invalid MCP path format: {mcp_path}. "
            "Expected format: 'module.path:variable_name'"
        )

    module_path, variable_name = mcp_path.split(":", 1)

    try:
        module = importlib.import_module(module_path)
    except ImportError:
        # If direct import fails, try loading as file path
        try:
            full_path = get_filepath(
                module_path if module_path.endswith(".py") else module_path + ".py"
            )
        except FileNotFoundError:
            raise ImportError(f"Cannot import module: {module_path}")

        if full_path.exists():
            spec = importlib.util.spec_from_file_location("custom_mcp", full_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module from {full_path}")
            module = importlib.util.module_from_spec(spec)
            sys.modules["custom_mcp"] = module
            spec.loader.exec_module(module)
        else:
            raise ImportError(f"Cannot import module: {module_path}")

    if not hasattr(module, variable_name):
        raise ValueError(
            f"Variable '{variable_name}' not found in module '{module_path}'"
        )
    mcp_instance = getattr(module, variable_name)

    if not isinstance(mcp_instance, FastMCP):
        from mcp.server.fastmcp import FastMCP as FastMCPv1

        if isinstance(mcp_instance, FastMCPv1):
            raise TypeError(
                f"Object at {mcp_path} is not a FastMCP v2 instance. "
                f"Got a FastMCP v1 instance instead. "
                "Please upgrade your MCP server to FastMCP v2."
            )
        raise TypeError(
            f"Object at {mcp_path} is not a FastMCP instance. "
            f"Got {type(mcp_instance).__name__}"
        )

    return mcp_instance


def _custom_list_rule(component_type: str, component_names: list[str]) -> schemas.Rule:
    return schemas.Rule(
        name=f"list-{component_type}",
        description=f"List all {component_type} (tip: exclude from `attributes.name`'s values the ones that you want to hide from the MCP client)",
        effect=enums.PolicyEffect.ALLOW,
        principal_conditions=[],
        resource_conditions=[
            schemas.Condition(
                path="attributes.component_type",
                operator=enums.ConditionOperator.EQUALS,
                value=component_type,
            ),
            schemas.Condition(
                path="attributes.name",
                operator=enums.ConditionOperator.IN,
                value=component_names,
            ),
        ],
        actions=["list"],
    )


def _custom_execute_rules(
    component_type: str, components: list[FastMCPComponent]
) -> list[schemas.Rule]:
    rules = []
    for component in components:
        rules.append(
            schemas.Rule(
                name=f"execute-{component_type}-{component.name}",
                description=f"Execute {component_type}:{component.name} (tip: add additional conditions on `attributes.arguments.[:path]` to restrict this execution)",
                effect=enums.PolicyEffect.ALLOW,
                principal_conditions=[],
                resource_conditions=[
                    schemas.Condition(
                        path="attributes.component_type",
                        operator=enums.ConditionOperator.EQUALS,
                        value=component_type,
                    ),
                    schemas.Condition(
                        path="attributes.name",
                        operator=enums.ConditionOperator.EQUALS,
                        value=component.name,
                    ),
                ],
                actions=["execute"],
            )
        )
    return rules


async def generate_custom_policy_from_mcp(mcp: FastMCP) -> schemas.Policy:
    """
    Generate a custom policy by analyzing the content of an MCP server.

    Args:
        mcp: the MCP server

    Returns:
        A policy object
    """
    rules: list[schemas.Rule] = []

    tools, resources, prompts = await asyncio.gather(
        mcp.get_tools(), mcp.get_resources(), mcp.get_prompts()
    )

    if tools:
        rules.extend(
            [_custom_list_rule("tools", list(tools.keys()))]
            + _custom_execute_rules("tools", list(tools.values()))
        )
    if resources:
        rules.extend(
            [_custom_list_rule("resources", list(resources.keys()))]
            + _custom_execute_rules("resources", list(resources.values()))
        )
    if prompts:
        rules.extend(
            [_custom_list_rule("prompts", list(prompts.keys()))]
            + _custom_execute_rules("prompts", list(prompts.values()))
        )

    return schemas.Policy(
        version="1.0",
        name=f"{mcp.name}-generated-policy",
        description=f"Generated policy for MCP server: {mcp.name}",
        default_effect=enums.PolicyEffect.DENY,
        rules=rules,
    )
