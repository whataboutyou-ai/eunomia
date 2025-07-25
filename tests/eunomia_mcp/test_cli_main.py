import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

from eunomia_core import enums, schemas
from eunomia_mcp.cli.main import app
from eunomia_mcp.cli.utils import DEFAULT_POLICY, SAMPLE_SERVER_CODE
from fastmcp import FastMCP


class TestInitCommand:
    """Test the init command."""

    def test_init_default_policy_file(self, runner, temp_dir):
        """Test init command with default policy file."""
        os.chdir(temp_dir)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert "Generated policy configuration file: mcp_policies.json" in result.stdout
        assert Path("mcp_policies.json").exists()

        with open("mcp_policies.json") as f:
            policy = json.load(f)
        assert policy == DEFAULT_POLICY.model_dump(exclude_none=True)

    def test_init_custom_policy_file(self, runner, temp_dir):
        """Test init command with custom policy file path."""
        os.chdir(temp_dir)
        result = runner.invoke(app, ["init", "--policy-file", "custom_policy.json"])

        assert result.exit_code == 0
        assert (
            "Generated policy configuration file: custom_policy.json" in result.stdout
        )
        assert Path("custom_policy.json").exists()

    def test_init_with_sample_server(self, runner, temp_dir):
        """Test init command with sample server generation."""
        os.chdir(temp_dir)
        result = runner.invoke(app, ["init", "--sample"])

        assert result.exit_code == 0
        assert "Generated policy configuration file: mcp_policies.json" in result.stdout
        assert "Generated sample server: mcp_server.py" in result.stdout
        assert Path("mcp_policies.json").exists()
        assert Path("mcp_server.py").exists()

        with open("mcp_server.py") as f:
            content = f.read()
        assert content == SAMPLE_SERVER_CODE

    def test_init_with_custom_sample_file(self, runner, temp_dir):
        """Test init command with custom sample file path."""
        os.chdir(temp_dir)
        result = runner.invoke(
            app, ["init", "--sample", "--sample-file", "custom_server.py"]
        )

        assert result.exit_code == 0
        assert "Generated sample server: custom_server.py" in result.stdout
        assert Path("custom_server.py").exists()

    def test_init_file_exists_without_force(self, runner, temp_dir):
        """Test init command when file exists without force flag."""
        os.chdir(temp_dir)
        policy_file = Path("existing_policy.json")
        policy_file.write_text('{"existing": "policy"}')

        result = runner.invoke(app, ["init", "--policy-file", "existing_policy.json"])

        assert result.exit_code == 1
        assert "already exists. Use --force to overwrite" in result.stdout

    def test_init_file_exists_with_force(self, runner, temp_dir):
        """Test init command when file exists with force flag."""
        os.chdir(temp_dir)
        policy_file = Path("existing_policy.json")
        policy_file.write_text('{"existing": "policy"}')

        result = runner.invoke(
            app, ["init", "--policy-file", "existing_policy.json", "--force"]
        )

        assert result.exit_code == 0
        assert (
            "Generated policy configuration file: existing_policy.json" in result.stdout
        )

        with open("existing_policy.json") as f:
            policy = json.load(f)
        assert policy == DEFAULT_POLICY.model_dump(exclude_none=True)

    def test_init_shows_next_steps(self, runner, temp_dir):
        """Test that init command shows next steps."""
        os.chdir(temp_dir)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert "Next steps:" in result.stdout
        assert "Review and customize the policy configuration file" in result.stdout
        assert "Start the Eunomia server" in result.stdout
        assert "Push the policy configuration file to Eunomia" in result.stdout
        assert "Run your MCP server with authorization" in result.stdout

    @patch("eunomia_mcp.cli.main.load_mcp_instance")
    @patch(
        "eunomia_mcp.cli.main.generate_custom_policy_from_mcp", new_callable=AsyncMock
    )
    def test_init_with_custom_mcp_success(
        self, mock_generate_policy, mock_load_mcp, runner, temp_dir
    ):
        """Test init command with successful custom MCP policy generation."""
        os.chdir(temp_dir)

        # Create real FastMCP instance
        mcp = FastMCP("test-mcp-server")

        @mcp.tool()
        def add(a: int, b: int) -> int:
            """Add two numbers"""
            return a + b

        mock_load_mcp.return_value = mcp

        # Mock generated policy
        custom_policy = schemas.Policy(
            version="1.0",
            name="test-custom-policy",
            description="Custom policy for test server",
            default_effect=enums.PolicyEffect.DENY,
            rules=[],
        )

        mock_generate_policy.return_value = custom_policy

        result = runner.invoke(app, ["init", "--custom-mcp", "test.module:mcp"])

        assert result.exit_code == 0
        assert (
            "Generated custom policy from MCP server: test-mcp-server" in result.stdout
        )
        assert "Generated policy configuration file: mcp_policies.json" in result.stdout

        mock_load_mcp.assert_called_once_with("test.module:mcp")

        # Verify the policy file contains the custom policy
        with open("mcp_policies.json") as f:
            policy_data = json.load(f)
        assert policy_data["name"] == "test-custom-policy"

    @patch("eunomia_mcp.cli.main.load_mcp_instance")
    def test_init_with_custom_mcp_load_error(self, mock_load_mcp, runner, temp_dir):
        """Test init command with MCP loading error."""
        os.chdir(temp_dir)
        mock_load_mcp.side_effect = ImportError("Cannot import module: test.module")

        result = runner.invoke(app, ["init", "--custom-mcp", "test.module:mcp"])

        assert result.exit_code == 1
        assert (
            "Error generating custom policy: Cannot import module: test.module"
            in result.stdout
        )
        mock_load_mcp.assert_called_once_with("test.module:mcp")

    @patch("eunomia_mcp.cli.main.load_mcp_instance")
    @patch(
        "eunomia_mcp.cli.main.generate_custom_policy_from_mcp", new_callable=AsyncMock
    )
    def test_init_with_custom_mcp_policy_generation_error(
        self, mock_generate_policy, mock_load_mcp, runner, temp_dir
    ):
        """Test init command with policy generation error."""
        os.chdir(temp_dir)

        mcp = FastMCP("test-server")
        mock_load_mcp.return_value = mcp

        mock_generate_policy.side_effect = Exception("Policy generation failed")

        result = runner.invoke(app, ["init", "--custom-mcp", "test.module:mcp"])

        assert result.exit_code == 1
        assert (
            "Error generating custom policy: Policy generation failed" in result.stdout
        )

    @patch("eunomia_mcp.cli.main.load_mcp_instance")
    @patch(
        "eunomia_mcp.cli.main.generate_custom_policy_from_mcp", new_callable=AsyncMock
    )
    def test_init_with_custom_mcp_and_sample(
        self, mock_generate_policy, mock_load_mcp, runner, temp_dir
    ):
        """Test init command with custom MCP and sample server generation."""
        os.chdir(temp_dir)

        mcp = FastMCP("test-server")

        @mcp.tool()
        def multiply(x: int, y: int) -> int:
            """Multiply two numbers"""
            return x * y

        mock_load_mcp.return_value = mcp

        custom_policy = DEFAULT_POLICY.model_copy()
        custom_policy.name = "custom-test-policy"

        mock_generate_policy.return_value = custom_policy

        result = runner.invoke(
            app, ["init", "--custom-mcp", "test.module:mcp", "--sample"]
        )

        assert result.exit_code == 0
        assert "Generated custom policy from MCP server: test-server" in result.stdout
        assert "Generated sample server: mcp_server.py" in result.stdout
        assert Path("mcp_policies.json").exists()
        assert Path("mcp_server.py").exists()


class TestValidateCommand:
    """Test the validate command."""

    def test_validate_valid_policy(self, runner, sample_policy_file):
        """Test validate command with valid policy file."""
        result = runner.invoke(app, ["validate", str(sample_policy_file)])

        assert result.exit_code == 0
        assert f"Policy file {sample_policy_file} is valid" in result.stdout
        assert "Found %d rules" % len(DEFAULT_POLICY.rules) in result.stdout

    def test_validate_invalid_policy(self, runner, invalid_policy_file):
        """Test validate command with invalid policy file."""
        result = runner.invoke(app, ["validate", str(invalid_policy_file)])

        assert result.exit_code == 1
        assert "Error validating policy:" in result.stdout

    def test_validate_nonexistent_file(self, runner):
        """Test validate command with nonexistent file."""
        result = runner.invoke(app, ["validate", "nonexistent.json"])

        assert result.exit_code == 1
        assert "Error validating policy:" in result.stdout

    def test_validate_malformed_json(self, runner, temp_dir):
        """Test validate command with malformed JSON."""
        policy_file = temp_dir / "malformed.json"
        policy_file.write_text('{"invalid": json}')

        result = runner.invoke(app, ["validate", str(policy_file)])

        assert result.exit_code == 1
        assert "Error validating policy:" in result.stdout


class TestPushCommand:
    """Test the push command."""

    @patch("eunomia_mcp.cli.main.EunomiaClient")
    def test_push_policy_success(
        self, mock_client_class, runner, sample_policy_file, mock_eunomia_client
    ):
        """Test successful policy push."""
        mock_client_class.return_value = mock_eunomia_client

        result = runner.invoke(app, ["push", str(sample_policy_file)])

        assert result.exit_code == 0
        assert f"Policy file {sample_policy_file} pushed to Eunomia" in result.stdout
        mock_client_class.assert_called_once_with(endpoint=None, api_key=None)

    @patch("eunomia_mcp.cli.main.EunomiaClient")
    def test_push_policy_with_custom_endpoint(
        self, mock_client_class, runner, sample_policy_file, mock_eunomia_client
    ):
        """Test policy push with custom endpoint."""
        mock_client_class.return_value = mock_eunomia_client

        result = runner.invoke(
            app,
            [
                "push",
                str(sample_policy_file),
                "--eunomia-endpoint",
                "https://custom.eunomia.dev",
                "--eunomia-api-key",
                "test-key",
            ],
        )

        assert result.exit_code == 0
        mock_client_class.assert_called_once_with(
            endpoint="https://custom.eunomia.dev", api_key="test-key"
        )

    @patch("eunomia_mcp.cli.main.EunomiaClient")
    @patch("eunomia_mcp.cli.main.typer.confirm")
    def test_push_policy_with_overwrite_confirmed(
        self,
        mock_confirm,
        mock_client_class,
        runner,
        sample_policy_file,
        mock_eunomia_client,
    ):
        """Test policy push with overwrite confirmation."""
        mock_confirm.return_value = True
        mock_client_class.return_value = mock_eunomia_client

        result = runner.invoke(app, ["push", str(sample_policy_file), "--overwrite"])

        assert result.exit_code == 0
        mock_confirm.assert_called_once()

    @patch("eunomia_mcp.cli.main.EunomiaClient")
    @patch("eunomia_mcp.cli.main.typer.confirm")
    def test_push_policy_with_overwrite_aborted(
        self,
        mock_confirm,
        mock_client_class,
        runner,
        sample_policy_file,
        mock_eunomia_client,
    ):
        """Test policy push with overwrite aborted."""
        mock_confirm.return_value = False
        mock_client_class.return_value = mock_eunomia_client

        result = runner.invoke(app, ["push", str(sample_policy_file), "--overwrite"])

        assert result.exit_code == 1
        mock_confirm.assert_called_once()

    @patch("eunomia_mcp.cli.main.EunomiaClient")
    def test_push_policy_client_error(
        self, mock_client_class, runner, sample_policy_file
    ):
        """Test policy push with client error."""
        mock_client_class.side_effect = Exception("Connection failed")

        result = runner.invoke(app, ["push", str(sample_policy_file)])

        assert result.exit_code == 1
        assert "Error pushing policy: Connection failed" in result.stdout

    def test_push_invalid_policy_file(self, runner, invalid_policy_file):
        """Test push command with invalid policy file."""
        result = runner.invoke(app, ["push", str(invalid_policy_file)])

        assert result.exit_code == 1
        assert "Error pushing policy:" in result.stdout

    def test_push_nonexistent_file(self, runner):
        """Test push command with nonexistent file."""
        result = runner.invoke(app, ["push", "nonexistent.json"])

        assert result.exit_code == 1
        assert "Error pushing policy:" in result.stdout


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Eunomia MCP Authorization Middleware CLI" in result.stdout
        assert "init" in result.stdout
        assert "validate" in result.stdout
        assert "push" in result.stdout

    def test_init_command_help(self, runner):
        """Test init command help."""
        result = runner.invoke(app, ["init", "--help"])

        assert result.exit_code == 0
        assert (
            "Initialize a new MCP project with Eunomia authorization" in result.stdout
        )

    def test_validate_command_help(self, runner):
        """Test validate command help."""
        result = runner.invoke(app, ["validate", "--help"])

        assert result.exit_code == 0
        assert "Validate a policy configuration file" in result.stdout

    def test_push_command_help(self, runner):
        """Test push command help."""
        result = runner.invoke(app, ["push", "--help"])

        assert result.exit_code == 0
        assert (
            "Push a policy configuration file to a remote Eunomia server"
            in result.stdout
        )

    def test_no_args_shows_help(self, runner):
        """Test that CLI shows help when no arguments provided."""
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "Eunomia MCP Authorization Middleware CLI" in result.stdout
