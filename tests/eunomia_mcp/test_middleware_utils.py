import json
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
from eunomia_core import schemas
from eunomia_mcp.middleware import EunomiaMcpMiddleware
from eunomia_mcp.utils import (
    _get_external_caller_directory,
    create_eunomia_middleware,
    get_filepath,
    load_policy_config,
)
from pydantic import ValidationError


class TestLoadPolicyConfig:
    """Test suite for load_policy_config function."""

    def test_load_valid_policy_config(self, sample_policy_file):
        """Test loading a valid policy configuration file."""
        policy = load_policy_config(str(sample_policy_file))

        assert isinstance(policy, schemas.Policy)
        assert policy.name == "mcp-default-policy"
        assert policy.version == "1.0"

    def test_load_policy_config_with_mock_file(self):
        """Test loading policy config with mocked file content."""
        valid_policy_data = {"name": "Test Policy", "version": "1.0.0", "rules": []}

        with patch("builtins.open", mock_open(read_data=json.dumps(valid_policy_data))):
            with patch("eunomia_mcp.utils.get_filepath") as mock_get_filepath:
                mock_get_filepath.return_value = Path("/mock/path/policy.json")

                policy = load_policy_config("mock_policy.json")

                assert isinstance(policy, schemas.Policy)
                assert policy.name == "test-policy"  # Slugified name
                assert policy.version == "1.0.0"

    def test_load_policy_config_file_not_found(self):
        """Test loading policy config when file doesn't exist."""
        with patch("eunomia_mcp.utils.get_filepath") as mock_get_filepath:
            mock_get_filepath.side_effect = FileNotFoundError("Policy file not found")

            with pytest.raises(FileNotFoundError, match="Policy file not found"):
                load_policy_config("nonexistent.json")

    def test_load_policy_config_invalid_json(self):
        """Test loading policy config with invalid JSON."""
        invalid_json = "{ invalid json content"

        with patch("builtins.open", mock_open(read_data=invalid_json)):
            with patch("eunomia_mcp.utils.get_filepath") as mock_get_filepath:
                mock_get_filepath.return_value = Path("/mock/path/policy.json")

                with pytest.raises(
                    ValidationError
                ):  # Pydantic raises ValidationError for invalid JSON
                    load_policy_config("invalid.json")

    def test_load_policy_config_invalid_schema(self):
        """Test loading policy config with invalid schema."""
        invalid_policy_data = {"invalid": "schema"}

        with patch(
            "builtins.open", mock_open(read_data=json.dumps(invalid_policy_data))
        ):
            with patch("eunomia_mcp.utils.get_filepath") as mock_get_filepath:
                mock_get_filepath.return_value = Path("/mock/path/policy.json")

                with pytest.raises(ValidationError):
                    load_policy_config("invalid_schema.json")


class TestGetFilepath:
    """Test suite for get_filepath function."""

    def test_strategy_1_absolute_path_exists(self, temp_dir):
        """Test strategy 1: absolute path that exists."""
        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')

        result = get_filepath(str(test_file))

        assert result == test_file.resolve()

    def test_strategy_1_relative_path_exists(self, temp_dir):
        """Test strategy 1: relative path that exists in current location."""
        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')

        # Mock Path to control exists() behavior for strategy 1
        original_path = Path

        class MockPath(original_path):
            def __new__(cls, *args, **kwargs):
                instance = original_path.__new__(cls, *args, **kwargs)
                return instance

            def exists(self):
                # Make relative path exist directly (strategy 1)
                return str(self) == "test.json"

            def resolve(self):
                if str(self) == "test.json":
                    return test_file.resolve()
                return super().resolve()

        with patch("eunomia_mcp.utils.Path", MockPath):
            result = get_filepath("test.json")
            assert result == test_file.resolve()

    @patch("pathlib.Path.cwd")
    def test_strategy_2_relative_to_cwd(self, mock_cwd, temp_dir):
        """Test strategy 2: relative to current working directory."""
        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')
        mock_cwd.return_value = temp_dir

        # Use a different working directory for the test
        with patch("os.getcwd", return_value="/different/directory"):
            result = get_filepath("test.json")
            assert result == test_file.resolve()

    @patch("pathlib.Path.cwd")
    def test_strategy_2_cwd_exception(self, mock_cwd, temp_dir):
        """Test strategy 2: handle exception when CWD doesn't exist."""
        mock_cwd.side_effect = OSError("Current directory not available")

        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')

        with patch(
            "eunomia_mcp.utils._get_external_caller_directory"
        ) as mock_caller_dir:
            mock_caller_dir.return_value = temp_dir

            # Mock Path constructor to control exists() behavior
            original_path = Path

            class MockPath(original_path):
                def __new__(cls, *args, **kwargs):
                    instance = original_path.__new__(cls, *args, **kwargs)
                    return instance

                def exists(self):
                    # Only return True for the caller directory path
                    return str(self) == str(temp_dir / "test.json")

            with patch("eunomia_mcp.utils.Path", MockPath):
                result = get_filepath("test.json")
                assert result == test_file.resolve()

    def test_strategy_3_relative_to_caller(self, temp_dir):
        """Test strategy 3: relative to external caller's directory."""
        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')

        with patch(
            "eunomia_mcp.utils._get_external_caller_directory"
        ) as mock_caller_dir:
            mock_caller_dir.return_value = temp_dir

            # Mock Path to control exists() behavior for different strategies
            original_path = Path

            class MockPath(original_path):
                def __new__(cls, *args, **kwargs):
                    instance = original_path.__new__(cls, *args, **kwargs)
                    return instance

                def exists(self):
                    # Return False for direct path and CWD, True for caller path
                    path_str = str(self)
                    if path_str == "test.json":
                        return False  # Direct path doesn't exist
                    elif "/different/directory" in path_str:
                        return False  # CWD path doesn't exist
                    elif str(temp_dir) in path_str and "test.json" in path_str:
                        return True  # Caller path exists
                    return False

            with patch("eunomia_mcp.utils.Path", MockPath):
                with patch("pathlib.Path.cwd") as mock_cwd:
                    mock_cwd.return_value = Path("/different/directory")

                    result = get_filepath("test.json")
                    assert result == test_file.resolve()

    def test_strategy_4_file_not_found_anywhere(self, temp_dir):
        """Test strategy 4: file not found in any location."""
        with patch(
            "eunomia_mcp.utils._get_external_caller_directory"
        ) as mock_caller_dir:
            mock_caller_dir.return_value = temp_dir

            # Mock Path to always return False for exists() and handle resolve() calls
            original_path = Path

            class MockPath(original_path):
                def __new__(cls, *args, **kwargs):
                    instance = original_path.__new__(cls, *args, **kwargs)
                    return instance

                def exists(self):
                    return False

                def resolve(self):
                    # Handle resolve() calls safely to avoid CWD issues
                    try:
                        return super().resolve()
                    except (OSError, FileNotFoundError):
                        # Return a mock resolved path to avoid errors
                        return Path("/mock/resolved") / self.name

            with patch("eunomia_mcp.utils.Path", MockPath):
                with patch("pathlib.Path.cwd") as mock_cwd:
                    mock_cwd.return_value = Path("/different/directory")

                    with pytest.raises(FileNotFoundError) as exc_info:
                        get_filepath("nonexistent.json")

                    error_message = str(exc_info.value)
                    assert "Policy file not found. Tried:" in error_message
                    assert "As provided:" in error_message
                    assert "Relative to CWD:" in error_message
                    assert "Relative to caller:" in error_message

    def test_strategy_4_cwd_not_available_error_message(self, temp_dir):
        """Test strategy 4: error message when CWD is not available."""
        with patch(
            "eunomia_mcp.utils._get_external_caller_directory"
        ) as mock_caller_dir:
            mock_caller_dir.return_value = temp_dir

            # Mock Path to always return False for exists() and handle resolve() calls
            original_path = Path

            class MockPath(original_path):
                def __new__(cls, *args, **kwargs):
                    instance = original_path.__new__(cls, *args, **kwargs)
                    return instance

                def exists(self):
                    return False

                def resolve(self):
                    # Handle resolve() calls safely
                    try:
                        return super().resolve()
                    except (OSError, FileNotFoundError):
                        return Path("/mock/resolved") / self.name

            with patch("eunomia_mcp.utils.Path", MockPath):
                with patch("pathlib.Path.cwd") as mock_cwd:
                    mock_cwd.side_effect = OSError("Directory not available")

                    with pytest.raises(FileNotFoundError) as exc_info:
                        get_filepath("nonexistent.json")

                    error_message = str(exc_info.value)
                    assert "current directory not available" in error_message


class TestGetExternalCallerDirectory:
    """Test suite for _get_external_caller_directory function."""

    def test_find_external_caller(self):
        """Test finding external caller directory."""
        # Mock the inspect.currentframe() to simulate call stack
        with patch("inspect.currentframe") as mock_currentframe:
            # Create mock frames
            frame1 = Mock()
            frame1.f_code.co_filename = "/path/to/eunomia_mcp/utils.py"
            frame1.f_back = None

            frame2 = Mock()
            frame2.f_code.co_filename = "/path/to/external/caller.py"
            frame2.f_back = frame1

            frame3 = Mock()
            frame3.f_code.co_filename = "/path/to/another/external/file.py"
            frame3.f_back = frame2

            mock_currentframe.return_value = frame3

            result = _get_external_caller_directory()

            # Should return the directory of the first non-eunomia_mcp file (frame2)
            assert result == Path("/path/to/external")

    def test_fallback_to_immediate_caller(self):
        """Test fallback when no external caller is found."""
        with patch("inspect.currentframe") as mock_currentframe:
            # Create mock frames where all are from eunomia_mcp
            frame1 = Mock()
            frame1.f_code.co_filename = "/path/to/eunomia_mcp/utils.py"
            frame1.f_back = None

            frame2 = Mock()
            frame2.f_code.co_filename = "/path/to/eunomia_mcp/middleware.py"
            frame2.f_back = frame1

            # Mock the immediate caller frame
            caller_frame = Mock()
            caller_frame.f_code.co_filename = "/path/to/immediate/caller.py"

            mock_currentframe.return_value = frame2
            mock_currentframe.return_value.f_back = caller_frame

            result = _get_external_caller_directory()

            assert result == Path("/path/to/immediate")

    def test_no_frames_available(self):
        """Test behavior when no frames are available."""
        with patch("inspect.currentframe") as mock_currentframe:
            mock_currentframe.return_value = None

            # This should raise an AttributeError when trying to access f_back
            with pytest.raises(AttributeError):
                _get_external_caller_directory()


class TestCreateEunomiaMiddleware:
    """Test suite for create_eunomia_middleware function."""

    @patch("eunomia_mcp.utils.EunomiaClient")
    def test_create_middleware_remote_mode(self, mock_client_class):
        """Test creating middleware in remote (CLIENT) mode."""
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        result = create_eunomia_middleware(
            use_remote_eunomia=True,
            eunomia_endpoint="http://example.com:8421",
            enable_audit_logging=False,
        )

        assert isinstance(result, EunomiaMcpMiddleware)
        mock_client_class.assert_called_once_with(endpoint="http://example.com:8421")

    @patch("eunomia_mcp.utils.EunomiaServer")
    @patch("eunomia_mcp.utils.load_policy_config")
    @patch("eunomia_mcp.utils.settings")
    def test_create_middleware_server_mode(
        self, mock_settings, mock_load_policy, mock_server_class
    ):
        """Test creating middleware in server (local) mode."""
        mock_server_instance = Mock()
        mock_server_class.return_value = mock_server_instance

        mock_policy = Mock(spec=schemas.Policy)
        mock_load_policy.return_value = mock_policy

        result = create_eunomia_middleware(
            policy_file="test_policy.json",
            use_remote_eunomia=False,
            enable_audit_logging=True,
        )

        assert isinstance(result, EunomiaMcpMiddleware)
        mock_load_policy.assert_called_once_with("test_policy.json")
        mock_server_instance.engine.add_policy.assert_called_once_with(mock_policy)

        # Verify settings were configured
        assert mock_settings.ENGINE_SQL_DATABASE is False
        assert mock_settings.FETCHERS == {}

    def test_create_middleware_remote_with_policy_file_error(self):
        """Test error when providing policy_file with remote Eunomia."""
        with pytest.raises(
            ValueError,
            match="policy_file is not supported when using a remote Eunomia server",
        ):
            create_eunomia_middleware(
                policy_file="test_policy.json", use_remote_eunomia=True
            )

    @patch("eunomia_mcp.utils.EunomiaServer")
    @patch("eunomia_mcp.utils.load_policy_config")
    @patch("eunomia_mcp.utils.settings")
    def test_create_middleware_default_policy_file(
        self, mock_settings, mock_load_policy, mock_server_class
    ):
        """Test creating middleware with default policy file."""
        mock_server_instance = Mock()
        mock_server_class.return_value = mock_server_instance

        mock_policy = Mock(spec=schemas.Policy)
        mock_load_policy.return_value = mock_policy

        result = create_eunomia_middleware()

        assert isinstance(result, EunomiaMcpMiddleware)
        mock_load_policy.assert_called_once_with("mcp_policies.json")

    @patch("eunomia_mcp.utils.EunomiaClient")
    def test_create_middleware_remote_default_endpoint(self, mock_client_class):
        """Test creating middleware with remote mode and default endpoint."""
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        result = create_eunomia_middleware(use_remote_eunomia=True)

        assert isinstance(result, EunomiaMcpMiddleware)
        mock_client_class.assert_called_once_with(endpoint=None)

    @patch("eunomia_mcp.utils.EunomiaServer")
    @patch("eunomia_mcp.utils.load_policy_config")
    @patch("eunomia_mcp.utils.settings")
    def test_create_middleware_custom_policy_file(
        self, mock_settings, mock_load_policy, mock_server_class
    ):
        """Test creating middleware with custom policy file."""
        mock_server_instance = Mock()
        mock_server_class.return_value = mock_server_instance

        mock_policy = Mock(spec=schemas.Policy)
        mock_load_policy.return_value = mock_policy

        result = create_eunomia_middleware(
            policy_file="custom_policy.json", enable_audit_logging=False
        )

        assert isinstance(result, EunomiaMcpMiddleware)
        mock_load_policy.assert_called_once_with("custom_policy.json")


# Integration tests for edge cases
class TestUtilsIntegration:
    """Integration tests for utils module."""

    def test_load_policy_config_integration(self, sample_policy_file):
        """Test load_policy_config integration with real file."""
        policy = load_policy_config(str(sample_policy_file))

        assert isinstance(policy, schemas.Policy)
        assert hasattr(policy, "name")
        assert hasattr(policy, "version")

    def test_get_filepath_integration_with_temp_file(self, temp_dir):
        """Test get_filepath integration with real temporary file."""
        test_file = temp_dir / "integration_test.json"
        test_file.write_text('{"test": "integration"}')

        # Test with absolute path
        result = get_filepath(str(test_file))
        assert result.exists()
        assert result.name == "integration_test.json"

    def test_get_filepath_strategies_isolated(self, temp_dir):
        """Test get_filepath strategies with controlled environment."""
        test_file = temp_dir / "strategy_test.json"
        test_file.write_text('{"test": "strategies"}')

        # Test strategy 1 (absolute path)
        result = get_filepath(str(test_file))
        assert result == test_file.resolve()

        # Test strategy 2 (relative to CWD) with mocking instead of changing directory
        original_path = Path

        class MockPathForCWD(original_path):
            def __new__(cls, *args, **kwargs):
                instance = original_path.__new__(cls, *args, **kwargs)
                return instance

            def exists(self):
                # Direct path doesn't exist, but CWD path does
                if str(self) == "strategy_test.json":
                    return False  # Direct doesn't exist
                elif str(self).endswith(str(temp_dir / "strategy_test.json")):
                    return True  # CWD path exists
                return False

            def resolve(self):
                if str(self).endswith(str(temp_dir / "strategy_test.json")):
                    return test_file.resolve()
                return super().resolve()

        with patch("eunomia_mcp.utils.Path", MockPathForCWD):
            with patch("pathlib.Path.cwd") as mock_cwd:
                mock_cwd.return_value = temp_dir

                result = get_filepath("strategy_test.json")
                assert result.exists()
                assert result.name == "strategy_test.json"
