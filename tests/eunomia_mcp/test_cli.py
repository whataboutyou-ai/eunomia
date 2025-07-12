import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from eunomia_core import enums, schemas
from eunomia_mcp.cli.main import app
from eunomia_mcp.cli.utils import (
    DEFAULT_POLICY,
    SAMPLE_SERVER_CODE,
    load_policy_config,
    push_policy_config,
)
from eunomia_sdk.client import EunomiaClient
from typer.testing import CliRunner


class TestEunomiaCLI:
    """Test suite for Eunomia MCP CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_policy_file(self, temp_dir):
        """Create a sample policy file for testing."""
        policy_file = temp_dir / "test_policy.json"
        with open(policy_file, "w") as f:
            json.dump(DEFAULT_POLICY, f, indent=2)
        return policy_file

    @pytest.fixture
    def invalid_policy_file(self, temp_dir):
        """Create an invalid policy file for testing."""
        policy_file = temp_dir / "invalid_policy.json"
        with open(policy_file, "w") as f:
            json.dump({"invalid": "policy"}, f, indent=2)
        return policy_file

    @pytest.fixture
    def mock_eunomia_client(self):
        """Create mock Eunomia client."""
        client = Mock(spec=EunomiaClient)
        client.get_policies.return_value = []
        client.delete_policy.return_value = None
        client.create_policy.return_value = None
        return client


class TestInitCommand(TestEunomiaCLI):
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
        assert policy == DEFAULT_POLICY

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
        assert policy == DEFAULT_POLICY

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


class TestValidateCommand(TestEunomiaCLI):
    """Test the validate command."""

    def test_validate_valid_policy(self, runner, sample_policy_file):
        """Test validate command with valid policy file."""
        result = runner.invoke(app, ["validate", str(sample_policy_file)])

        assert result.exit_code == 0
        assert f"Policy file {sample_policy_file} is valid" in result.stdout
        assert "Found 2 rules" in result.stdout

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


class TestPushCommand(TestEunomiaCLI):
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


class TestCLIUtils:
    """Test CLI utility functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_policy_file(self, temp_dir):
        """Create a sample policy file for testing."""
        policy_file = temp_dir / "test_policy.json"
        with open(policy_file, "w") as f:
            json.dump(DEFAULT_POLICY, f, indent=2)
        return policy_file

    @pytest.fixture
    def mock_eunomia_client(self):
        """Create mock Eunomia client."""
        client = Mock(spec=EunomiaClient)
        client.get_policies.return_value = []
        client.delete_policy.return_value = None
        client.create_policy.return_value = None
        return client

    def test_load_policy_config_success(self, sample_policy_file):
        """Test successful policy loading."""
        policy = load_policy_config(str(sample_policy_file))

        assert isinstance(policy, schemas.Policy)
        assert policy.name == "mcp-default-policy"
        assert policy.version == "1.0"
        assert policy.default_effect == enums.PolicyEffect.DENY
        assert len(policy.rules) == 2

    def test_load_policy_config_file_not_found(self):
        """Test policy loading with nonexistent file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_policy_config("nonexistent.json")

        assert "Policy file not found: nonexistent.json" in str(exc_info.value)

    def test_load_policy_config_invalid_json(self, temp_dir):
        """Test policy loading with invalid JSON."""
        policy_file = temp_dir / "invalid.json"
        policy_file.write_text('{"invalid": json}')

        with pytest.raises(Exception):
            load_policy_config(str(policy_file))

    def test_load_policy_config_invalid_schema(self, temp_dir):
        """Test policy loading with invalid policy schema."""
        policy_file = temp_dir / "invalid_schema.json"
        policy_file.write_text('{"invalid": "schema"}')

        with pytest.raises(Exception):
            load_policy_config(str(policy_file))

    def test_push_policy_config_success(self, sample_policy_file, mock_eunomia_client):
        """Test successful policy push."""
        push_policy_config(str(sample_policy_file), False, mock_eunomia_client)

        mock_eunomia_client.create_policy.assert_called_once()
        mock_eunomia_client.get_policies.assert_not_called()
        mock_eunomia_client.delete_policy.assert_not_called()

    def test_push_policy_config_with_overwrite(
        self, sample_policy_file, mock_eunomia_client
    ):
        """Test policy push with overwrite."""
        existing_policy = Mock()
        existing_policy.name = "existing-policy"
        mock_eunomia_client.get_policies.return_value = [existing_policy]

        push_policy_config(str(sample_policy_file), True, mock_eunomia_client)

        mock_eunomia_client.get_policies.assert_called_once()
        mock_eunomia_client.delete_policy.assert_called_once_with("existing-policy")
        mock_eunomia_client.create_policy.assert_called_once()

    def test_push_policy_config_multiple_existing_policies(
        self, sample_policy_file, mock_eunomia_client
    ):
        """Test policy push with multiple existing policies to overwrite."""
        existing_policies = [Mock(name="policy1"), Mock(name="policy2")]
        existing_policies[0].name = "policy1"
        existing_policies[1].name = "policy2"
        mock_eunomia_client.get_policies.return_value = existing_policies

        push_policy_config(str(sample_policy_file), True, mock_eunomia_client)

        mock_eunomia_client.get_policies.assert_called_once()
        assert mock_eunomia_client.delete_policy.call_count == 2
        mock_eunomia_client.delete_policy.assert_any_call("policy1")
        mock_eunomia_client.delete_policy.assert_any_call("policy2")
        mock_eunomia_client.create_policy.assert_called_once()

    def test_push_policy_config_client_error(
        self, sample_policy_file, mock_eunomia_client
    ):
        """Test policy push with client error."""
        mock_eunomia_client.create_policy.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            push_policy_config(str(sample_policy_file), False, mock_eunomia_client)


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

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
        assert "Push a policy configuration file to Eunomia" in result.stdout

    def test_no_args_shows_help(self, runner):
        """Test that CLI shows help when no arguments provided."""
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "Eunomia MCP Authorization Middleware CLI" in result.stdout


class TestConstants:
    """Test CLI constants and defaults."""

    def test_default_policy_structure(self):
        """Test that DEFAULT_POLICY has correct structure."""
        assert DEFAULT_POLICY["version"] == "1.0"
        assert DEFAULT_POLICY["name"] == "mcp-default-policy"
        assert DEFAULT_POLICY["default_effect"] == enums.PolicyEffect.DENY
        assert len(DEFAULT_POLICY["rules"]) == 2

        # Check first rule
        discovery_rule = DEFAULT_POLICY["rules"][0]
        assert discovery_rule["name"] == "allow-mcp-discovery"
        assert discovery_rule["effect"] == enums.PolicyEffect.ALLOW
        assert discovery_rule["actions"] == ["access"]

        # Check second rule
        ops_rule = DEFAULT_POLICY["rules"][1]
        assert ops_rule["name"] == "allow-mcp-operations"
        assert ops_rule["effect"] == enums.PolicyEffect.ALLOW
        assert ops_rule["actions"] == ["execute", "read"]

    def test_sample_server_code_structure(self):
        """Test that SAMPLE_SERVER_CODE contains expected components."""
        assert "from fastmcp import FastMCP" in SAMPLE_SERVER_CODE
        assert "from eunomia_mcp import EunomiaMcpMiddleware" in SAMPLE_SERVER_CODE
        assert "EunomiaMcpMiddleware()" in SAMPLE_SERVER_CODE
        assert "@mcp.tool()" in SAMPLE_SERVER_CODE
        assert "def add(a: int, b: int) -> int:" in SAMPLE_SERVER_CODE
        assert "mcp.run" in SAMPLE_SERVER_CODE
