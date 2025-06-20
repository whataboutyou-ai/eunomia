import json
import os
from typing import Optional

import typer
from eunomia_sdk.client import EunomiaClient

from eunomia_mcp.cli.utils import (
    DEFAULT_POLICY,
    SAMPLE_SERVER_CODE,
    load_policy_config,
    push_policy_config,
)

app = typer.Typer(
    name="eunomia-mcp",
    help="Eunomia MCP Authorization Middleware CLI",
    no_args_is_help=True,
)


@app.command()
def init(
    policy_file: str = typer.Option(
        "mcp_policies.json",
        "--policy-file",
        help="Policy configuration file path",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing file",
    ),
    sample: bool = typer.Option(
        False,
        "--sample",
        help="Generate a sample MCP server with Eunomia authorization",
    ),
    sample_file: str = typer.Option(
        "mcp_server.py",
        "--sample-file",
        help="Sample MCP server file path",
    ),
):
    """
    Initialize a new MCP project with Eunomia authorization.

    This command generates a policy configuration file and, optionally, the code for a sample MCP server.
    """

    if os.path.exists(policy_file) and not force:
        typer.echo(
            f"Policy file {policy_file} already exists. Use --force to overwrite."
        )
        raise typer.Exit(1)

    with open(policy_file, "w") as f:
        json.dump(DEFAULT_POLICY, f, indent=2)
    typer.echo(f"Generated policy configuration file: {policy_file}")

    if sample:
        with open(sample_file, "w") as f:
            f.write(SAMPLE_SERVER_CODE)
        typer.echo(f"Generated sample server: {sample_file}")

    typer.echo("\nNext steps:")
    typer.echo("1. Review and customize the policy configuration file")
    typer.echo("2. Start the Eunomia server")
    typer.echo("3. Push the policy configuration file to Eunomia")
    typer.echo("4. Run your MCP server with authorization")


@app.command()
def validate(policy_file: str = typer.Argument(..., help="Policy file to validate")):
    """Validate a policy configuration file."""
    try:
        policy = load_policy_config(policy_file)
        typer.echo(f"Policy file {policy_file} is valid")
        typer.echo(f"Found {len(policy.rules)} rules")

    except Exception as e:
        typer.echo(f"Error validating policy: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def push(
    policy_file: str = typer.Argument(..., help="Policy file to push"),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing policies",
    ),
    eunomia_endpoint: Optional[str] = typer.Option(
        None,
        "--eunomia-endpoint",
        help="Eunomia server endpoint",
    ),
    eunomia_api_key: Optional[str] = typer.Option(
        None,
        "--eunomia-api-key",
        help="Eunomia server API key",
    ),
):
    """Push a policy configuration file to Eunomia."""
    if overwrite:
        if not typer.confirm(
            "Are you sure you want to push this policy to Eunomia "
            "and overwrite all existing policies? "
            "This action is destructive and cannot be undone."
        ):
            raise typer.Abort()

    try:
        client = EunomiaClient(endpoint=eunomia_endpoint, api_key=eunomia_api_key)
        push_policy_config(policy_file, overwrite, client)
        typer.echo(f"Policy file {policy_file} pushed to Eunomia")

    except Exception as e:
        typer.echo(f"Error pushing policy: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
