import os

from eunomia_core import enums, schemas
from eunomia_sdk import EunomiaClient

DEFAULT_POLICY = {
    "version": "1.0",
    "name": "mcp-default-policy",
    "description": "Default policy for a MCP server",
    "default_effect": enums.PolicyEffect.DENY,
    "rules": [
        {
            "name": "unrestricted-listing",
            "description": "All principals can list tools, resources, and prompts",
            "effect": enums.PolicyEffect.ALLOW,
            "principal_conditions": [],
            "resource_conditions": [],
            "actions": ["list"],
        },
        {
            "name": "unrestricted-execution",
            "description": "All principals can call tools, read resources, and get prompts",
            "effect": enums.PolicyEffect.ALLOW,
            "principal_conditions": [],
            "resource_conditions": [],
            "actions": ["call", "read", "get"],
        },
    ],
}

SAMPLE_SERVER_CODE = '''
from fastmcp import FastMCP
from eunomia_mcp import EunomiaMcpMiddleware

# Create your FastMCP server
mcp = FastMCP("Secure MCP Server 🔒")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add Eunomia authorization middleware
middleware = EunomiaMcpMiddleware()

# Create ASGI app with authorization
app = mcp.add_middleware(middleware)

if __name__ == "__main__":
    mcp.run()
'''


def load_policy_config(policy_file: str) -> schemas.Policy:
    """
    Load policy configuration from a JSON file.

    Args:
        policy_file: Path to policy configuration JSON file

    Returns:
        Policy configuration dictionary
    """
    if not os.path.exists(policy_file):
        raise FileNotFoundError(f"Policy file not found: {policy_file}")

    with open(policy_file, "r") as f:
        return schemas.Policy.model_validate_json(f.read())


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
