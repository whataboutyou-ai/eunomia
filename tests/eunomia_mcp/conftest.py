import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from eunomia_mcp.cli.utils import DEFAULT_POLICY
from eunomia_sdk.client import EunomiaClient
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_policy_file(temp_dir):
    """Create a sample policy file for testing."""
    policy_file = temp_dir / "test_policy.json"
    with open(policy_file, "w") as f:
        json.dump(DEFAULT_POLICY.model_dump(exclude_none=True), f, indent=2)
    return policy_file


@pytest.fixture
def invalid_policy_file(temp_dir):
    """Create an invalid policy file for testing."""
    policy_file = temp_dir / "invalid_policy.json"
    with open(policy_file, "w") as f:
        json.dump({"invalid": "policy"}, f, indent=2)
    return policy_file


@pytest.fixture
def mock_eunomia_client():
    """Create mock Eunomia client."""
    client = Mock(spec=EunomiaClient)
    client.get_policies.return_value = []
    client.delete_policy.return_value = None
    client.create_policy.return_value = None
    return client
