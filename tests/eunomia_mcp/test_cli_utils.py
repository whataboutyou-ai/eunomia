from unittest.mock import Mock, patch

import pytest
from eunomia_core import enums, schemas
from eunomia_mcp.cli.utils import (
    DEFAULT_POLICY,
    SAMPLE_SERVER_CODE,
    generate_custom_policy_from_mcp,
    load_mcp_instance,
    push_policy_config,
)
from fastmcp import FastMCP
from mcp.server.fastmcp import FastMCP as FastMCPv1


class TestCLIUtils:
    """Test CLI utility functions."""

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


class TestConstants:
    """Test CLI constants and defaults."""

    def test_default_policy_structure(self):
        """Test that DEFAULT_POLICY has correct structure."""
        assert DEFAULT_POLICY.version == "1.0"
        assert DEFAULT_POLICY.name == "mcp-default-policy"
        assert DEFAULT_POLICY.default_effect == enums.PolicyEffect.DENY
        assert len(DEFAULT_POLICY.rules) == 1

        # Check rule
        listing_rule = DEFAULT_POLICY.rules[0]
        assert listing_rule.name == "unrestricted-access"
        assert listing_rule.effect == enums.PolicyEffect.ALLOW
        assert listing_rule.actions == ["list", "execute"]

    def test_sample_server_code_structure(self):
        """Test that SAMPLE_SERVER_CODE contains expected components."""
        assert "from fastmcp import FastMCP" in SAMPLE_SERVER_CODE
        assert "from eunomia_mcp import create_eunomia_middleware" in SAMPLE_SERVER_CODE
        assert (
            'middleware = create_eunomia_middleware(policy_file="mcp_policies.json")'
            in SAMPLE_SERVER_CODE
        )
        assert "@mcp.tool()" in SAMPLE_SERVER_CODE
        assert "def add(a: int, b: int) -> int:" in SAMPLE_SERVER_CODE
        assert "mcp.run" in SAMPLE_SERVER_CODE


class TestLoadMcpInstance:
    """Test the load_mcp_instance function."""

    @patch("eunomia_mcp.cli.utils.importlib.import_module")
    def test_load_mcp_instance_success_module_import(self, mock_import_module):
        """Test successful MCP instance loading via module import."""
        # Create real FastMCP instance
        mcp = FastMCP("test-server")

        @mcp.tool()
        def test_tool() -> str:
            """A test tool"""
            return "test"

        # Create a simple mock module without any async attributes
        mock_module = type("MockModule", (), {})()
        mock_module.mcp = mcp
        mock_import_module.return_value = mock_module

        result = load_mcp_instance("test.module:mcp")

        assert result == mcp
        assert isinstance(result, FastMCP)
        mock_import_module.assert_called_once_with("test.module")

    @patch("eunomia_mcp.cli.utils.importlib.import_module")
    @patch("eunomia_mcp.cli.utils.os.path.exists")
    @patch("eunomia_mcp.cli.utils.importlib.util.spec_from_file_location")
    @patch("eunomia_mcp.cli.utils.importlib.util.module_from_spec")
    def test_load_mcp_instance_success_file_import(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_exists,
        mock_import_module,
    ):
        """Test successful MCP instance loading via file import."""
        # Mock import_module to fail initially
        mock_import_module.side_effect = ImportError("No module named 'test.file'")

        # Mock file exists
        mock_exists.return_value = True

        # Mock spec creation and module loading
        mock_spec = Mock()
        mock_loader = Mock()
        mock_spec.loader = mock_loader
        mock_spec_from_file.return_value = mock_spec

        # Create real FastMCP instance
        mcp = FastMCP("file-server")

        @mcp.resource("uri://test")
        def test_resource() -> str:
            """A test resource"""
            return "test resource"

        # Use a simple mock module without any async attributes
        mock_module = type("MockModule", (), {})()
        mock_module.mcp = mcp
        mock_module_from_spec.return_value = mock_module

        result = load_mcp_instance("test/file:mcp")

        assert result == mcp
        assert isinstance(result, FastMCP)
        mock_import_module.assert_called_once_with("test/file")
        mock_exists.assert_called_once_with("test/file.py")
        mock_spec_from_file.assert_called_once_with("custom_mcp", "test/file.py")
        mock_loader.exec_module.assert_called_once_with(mock_module)

    @patch("eunomia_mcp.cli.utils.importlib.import_module")
    @patch("eunomia_mcp.cli.utils.os.path.exists")
    @patch("eunomia_mcp.cli.utils.importlib.util.spec_from_file_location")
    @patch("eunomia_mcp.cli.utils.importlib.util.module_from_spec")
    def test_load_mcp_instance_success_file_import_with_py_extension(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_exists,
        mock_import_module,
    ):
        """Test successful MCP instance loading with .py extension."""
        mock_import_module.side_effect = ImportError("No module named 'test.file.py'")
        mock_exists.return_value = True

        mock_spec = Mock()
        mock_loader = Mock()
        mock_spec.loader = mock_loader
        mock_spec_from_file.return_value = mock_spec

        # Create real FastMCP instance
        mcp = FastMCP("py-server")

        @mcp.prompt("test-prompt")
        def test_prompt() -> str:
            """A test prompt"""
            return "test prompt"

        # Use a simple mock module without any async attributes
        mock_module = type("MockModule", (), {})()
        mock_module.server_instance = mcp
        mock_module_from_spec.return_value = mock_module

        result = load_mcp_instance("test/file.py:server_instance")

        assert result == mcp
        assert isinstance(result, FastMCP)
        mock_spec_from_file.assert_called_once_with("custom_mcp", "test/file.py")

    def test_load_mcp_instance_invalid_path_format(self):
        """Test load_mcp_instance with invalid path format."""
        with pytest.raises(ValueError) as exc_info:
            load_mcp_instance("invalid_path_without_colon")

        assert "Invalid MCP path format" in str(exc_info.value)
        assert "Expected format: 'module.path:variable_name'" in str(exc_info.value)

    @patch("eunomia_mcp.cli.utils.importlib.import_module")
    @patch("eunomia_mcp.cli.utils.os.path.exists")
    def test_load_mcp_instance_import_error_no_file(
        self, mock_exists, mock_import_module
    ):
        """Test load_mcp_instance with import error and no file fallback."""
        mock_import_module.side_effect = ImportError("No module named 'nonexistent'")
        mock_exists.return_value = False

        with pytest.raises(ImportError) as exc_info:
            load_mcp_instance("nonexistent.module:mcp")

        assert "Cannot import module: nonexistent.module" in str(exc_info.value)

    @patch("eunomia_mcp.cli.utils.importlib.import_module")
    def test_load_mcp_instance_variable_not_found(self, mock_import_module):
        """Test load_mcp_instance with missing variable in module."""
        # Create a simple mock module without any async attributes
        mock_module = type("MockModule", (), {})()
        mock_import_module.return_value = mock_module

        with pytest.raises(ValueError) as exc_info:
            load_mcp_instance("test.module:nonexistent_var")

        assert "Variable 'nonexistent_var' not found in module 'test.module'" in str(
            exc_info.value
        )

    @patch("eunomia_mcp.cli.utils.importlib.import_module")
    def test_load_mcp_instance_not_fastmcp_instance(self, mock_import_module):
        """Test load_mcp_instance with object that's not a FastMCP instance."""
        # Create a simple mock module without any async attributes
        mock_module = type("MockModule", (), {})()
        mock_module.not_mcp = "not an MCP instance"
        mock_import_module.return_value = mock_module

        with pytest.raises(TypeError) as exc_info:
            load_mcp_instance("test.module:not_mcp")

        assert "Object at test.module:not_mcp is not a FastMCP instance" in str(
            exc_info.value
        )
        assert "Got str" in str(exc_info.value)

    @patch("eunomia_mcp.cli.utils.importlib.import_module")
    def test_load_mcp_instance_fastmcp_v1_instance(self, mock_import_module):
        """Test load_mcp_instance with object that's a FastMCP v1 instance."""
        # Create a simple mock module without any async attributes
        mock_module = type("MockModule", (), {})()
        mock_module.mcp = FastMCPv1("test-server")
        mock_import_module.return_value = mock_module

        with pytest.raises(TypeError) as exc_info:
            load_mcp_instance("test.module:mcp")

        assert "Object at test.module:mcp is not a FastMCP v2 instance" in str(
            exc_info.value
        )
        assert "Got a FastMCP v1 instance instead" in str(exc_info.value)

    @patch("eunomia_mcp.cli.utils.importlib.import_module")
    @patch("eunomia_mcp.cli.utils.os.path.exists")
    @patch("eunomia_mcp.cli.utils.importlib.util.spec_from_file_location")
    def test_load_mcp_instance_spec_creation_failure(
        self, mock_spec_from_file, mock_exists, mock_import_module
    ):
        """Test load_mcp_instance with spec creation failure."""
        mock_import_module.side_effect = ImportError("No module")
        mock_exists.return_value = True
        mock_spec_from_file.return_value = None

        with pytest.raises(ImportError) as exc_info:
            load_mcp_instance("test/file:mcp")

        assert "Cannot load module from test/file.py" in str(exc_info.value)

    @patch("eunomia_mcp.cli.utils.importlib.import_module")
    @patch("eunomia_mcp.cli.utils.os.path.exists")
    @patch("eunomia_mcp.cli.utils.importlib.util.spec_from_file_location")
    def test_load_mcp_instance_no_loader(
        self, mock_spec_from_file, mock_exists, mock_import_module
    ):
        """Test load_mcp_instance with missing loader in spec."""
        mock_import_module.side_effect = ImportError("No module")
        mock_exists.return_value = True

        mock_spec = Mock()
        mock_spec.loader = None
        mock_spec_from_file.return_value = mock_spec

        with pytest.raises(ImportError) as exc_info:
            load_mcp_instance("test/file:mcp")

        assert "Cannot load module from test/file.py" in str(exc_info.value)


class TestGenerateCustomPolicyFromMcp:
    """Test the generate_custom_policy_from_mcp function."""

    @pytest.fixture
    def empty_mcp_server(self) -> FastMCP:
        """Create an empty FastMCP server for testing."""
        return FastMCP("empty-server")

    @pytest.fixture
    def simple_mcp_server(self) -> FastMCP:
        """Create a simple FastMCP server with one tool."""
        mcp = FastMCP("simple-server")

        @mcp.tool()
        def add(a: int, b: int) -> int:
            """Add two numbers"""
            return a + b

        return mcp

    @pytest.fixture
    def full_mcp_server(self) -> FastMCP:
        """Create FastMCP server with tools, resources, and prompts."""
        mcp = FastMCP("full-server")

        @mcp.tool()
        def calculate(x: int, y: int) -> int:
            """Calculate sum"""
            return x + y

        @mcp.resource("uri://test-resource")
        def get_resource() -> str:
            """Get test resource"""
            return "test data"

        @mcp.prompt("test-prompt")
        def get_prompt() -> str:
            """Get test prompt"""
            return "test prompt"

        return mcp

    @pytest.fixture
    def multi_tool_mcp_server(self) -> FastMCP:
        """Create FastMCP server with multiple tools."""
        mcp = FastMCP("multi-tools-server")

        @mcp.tool()
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers"""
            return a + b

        @mcp.tool()
        def multiply_numbers(x: int, y: int) -> int:
            """Multiply two numbers"""
            return x * y

        return mcp

    @pytest.mark.asyncio
    async def test_generate_custom_policy_empty_server(self, empty_mcp_server):
        """Test generating policy from server with no components."""
        policy = await generate_custom_policy_from_mcp(empty_mcp_server)

        assert policy.version == "1.0"
        assert policy.name == "empty-server-generated-policy"
        assert policy.description == "Generated policy for MCP server: empty-server"
        assert policy.default_effect == enums.PolicyEffect.DENY
        assert len(policy.rules) == 0

    @pytest.mark.asyncio
    async def test_generate_custom_policy_with_tools_only(self, simple_mcp_server):
        """Test generating policy from server with only tools."""
        policy = await generate_custom_policy_from_mcp(simple_mcp_server)

        assert policy.version == "1.0"
        assert policy.name == "simple-server-generated-policy"
        assert policy.default_effect == enums.PolicyEffect.DENY
        assert len(policy.rules) == 2  # 1 list rule + 1 execute rule

        # Check list rule
        list_rule = policy.rules[0]
        assert list_rule.name == "list-tools"
        assert list_rule.effect == enums.PolicyEffect.ALLOW
        assert list_rule.actions == ["list"]
        assert len(list_rule.resource_conditions) == 2

        # Check execute rule
        execute_rule = policy.rules[1]
        assert execute_rule.name == "execute-tools-add"
        assert execute_rule.effect == enums.PolicyEffect.ALLOW
        assert execute_rule.actions == ["execute"]

    @pytest.mark.asyncio
    async def test_generate_custom_policy_with_all_components(self, full_mcp_server):
        """Test generating policy from server with all component types."""
        policy = await generate_custom_policy_from_mcp(full_mcp_server)

        assert policy.version == "1.0"
        assert policy.name == "full-server-generated-policy"
        assert policy.default_effect == enums.PolicyEffect.DENY
        assert len(policy.rules) == 6  # 3 list rules + 3 execute rules

        # Verify rule names
        rule_names = [rule.name for rule in policy.rules]
        expected_names = [
            "list-tools",
            "execute-tools-calculate",
            "list-resources",
            "execute-resources-get_resource",
            "list-prompts",
            "execute-prompts-test-prompt",
        ]
        assert rule_names == expected_names

    @pytest.mark.asyncio
    async def test_generate_custom_policy_with_multiple_tools(
        self, multi_tool_mcp_server
    ):
        """Test generating policy from server with multiple tools."""
        policy = await generate_custom_policy_from_mcp(multi_tool_mcp_server)

        assert len(policy.rules) == 3  # 1 list rule + 2 execute rules

        # Check list rule includes both tools
        list_rule = policy.rules[0]
        name_condition = next(
            cond
            for cond in list_rule.resource_conditions
            if cond.path == "attributes.name"
        )
        assert set(name_condition.value) == {"add_numbers", "multiply_numbers"}

        # Check individual execute rules
        execute_rules = policy.rules[1:]
        assert len(execute_rules) == 2
        execute_rule_names = {rule.name for rule in execute_rules}
        expected_execute_names = {
            "execute-tools-add_numbers",
            "execute-tools-multiply_numbers",
        }
        assert execute_rule_names == expected_execute_names

    @pytest.mark.asyncio
    async def test_generate_custom_policy_rule_structure(self, simple_mcp_server):
        """Test the structure of generated rules."""
        policy = await generate_custom_policy_from_mcp(simple_mcp_server)

        list_rule = policy.rules[0]
        execute_rule = policy.rules[1]

        # Check list rule structure
        assert list_rule.effect == enums.PolicyEffect.ALLOW
        assert list_rule.principal_conditions == []
        assert len(list_rule.resource_conditions) == 2

        component_type_condition = list_rule.resource_conditions[0]
        assert component_type_condition.path == "attributes.component_type"
        assert component_type_condition.operator == enums.ConditionOperator.EQUALS
        assert component_type_condition.value == "tools"

        name_condition = list_rule.resource_conditions[1]
        assert name_condition.path == "attributes.name"
        assert name_condition.operator == enums.ConditionOperator.IN
        assert name_condition.value == ["add"]

        # Check execute rule structure
        assert execute_rule.effect == enums.PolicyEffect.ALLOW
        assert execute_rule.principal_conditions == []
        assert len(execute_rule.resource_conditions) == 2

        exec_component_type_condition = execute_rule.resource_conditions[0]
        assert exec_component_type_condition.path == "attributes.component_type"
        assert exec_component_type_condition.operator == enums.ConditionOperator.EQUALS
        assert exec_component_type_condition.value == "tools"

        exec_name_condition = execute_rule.resource_conditions[1]
        assert exec_name_condition.path == "attributes.name"
        assert exec_name_condition.operator == enums.ConditionOperator.EQUALS
        assert exec_name_condition.value == "add"

    def test_generate_custom_policy_sync_wrapper(self, empty_mcp_server):
        """Test that the function can be called synchronously using asyncio.run."""
        import asyncio

        policy = asyncio.run(generate_custom_policy_from_mcp(empty_mcp_server))

        assert isinstance(policy, schemas.Policy)
        assert policy.name == "empty-server-generated-policy"
