from unittest.mock import AsyncMock, Mock, patch

import pytest
from eunomia_core import enums, schemas

from eunomia.engine.opa_engine import OPAClient, OPAException, OPAPolicyEngine


@pytest.fixture
def sample_check_request():
    """Create a sample check request for testing."""
    return schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            uri="user://john.doe",
            attributes={"role": "user", "organization": "acme"},
            type=enums.EntityType.principal,
        ),
        resource=schemas.ResourceCheck(
            uri="doc://sensitive",
            attributes={"type": "document", "classification": "confidential"},
            type=enums.EntityType.resource,
        ),
        action="read",
    )


@pytest.fixture
def opa_engine():
    """Create an OPA engine instance for testing."""
    return OPAPolicyEngine(
        base_url="http://localhost:8181", policy_path="eunomia/allow", timeout=30
    )


@pytest.fixture
def opa_client():
    """Create an OPA client instance for testing."""
    return OPAClient(base_url="http://localhost:8181", timeout=30)


class TestOPAClient:
    """Test the OPA HTTP client."""

    @pytest.mark.asyncio
    async def test_evaluate_policy_success(self, opa_client):
        """Test successful policy evaluation."""

        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "result": {"allow": True, "reason": "Test allow"}
        }

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await opa_client.evaluate_policy(
                "eunomia/allow", {"principal": {"role": "admin"}}
            )

            assert result == {"result": {"allow": True, "reason": "Test allow"}}

    @pytest.mark.asyncio
    async def test_evaluate_policy_not_found(self, opa_client):
        """Test policy not found error."""

        # Mock 404 response
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text.return_value = "Policy not found"

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(
                OPAException, match="Policy path 'eunomia/allow' not found"
            ):
                await opa_client.evaluate_policy("eunomia/allow", {})

    @pytest.mark.asyncio
    async def test_evaluate_policy_server_error(self, opa_client):
        """Test server error handling."""

        # Mock 500 response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal server error"

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(
                OPAException, match="OPA request failed with status 500"
            ):
                await opa_client.evaluate_policy("eunomia/allow", {})


class TestOPAPolicyEngine:
    """Test the OPA policy engine."""

    def test_prepare_opa_input(self, opa_engine, sample_check_request):
        """Test conversion of CheckRequest to OPA input format."""
        opa_input = opa_engine._prepare_opa_input(sample_check_request)

        expected = {
            "principal": {
                "uri": "user://john.doe",
                "attributes": {"role": "user", "organization": "acme"},
                "type": "principal",
            },
            "resource": {
                "uri": "doc://sensitive",
                "attributes": {"type": "document", "classification": "confidential"},
                "type": "resource",
            },
            "action": "read",
        }

        assert opa_input == expected

    def test_parse_opa_response_boolean(self, opa_engine):
        """Test parsing boolean OPA response."""
        opa_response = {"result": True}

        result = opa_engine._parse_opa_response(opa_response)

        assert result.allowed is True
        assert "OPA policy evaluation result: True" in result.reason

    def test_parse_opa_response_structured(self, opa_engine):
        """Test parsing structured OPA response."""
        opa_response = {"result": {"allow": True, "reason": "Admin access granted"}}

        result = opa_engine._parse_opa_response(opa_response)

        assert result.allowed is True
        assert result.reason == "Admin access granted"

    def test_parse_opa_response_no_result(self, opa_engine):
        """Test parsing OPA response with no result."""
        opa_response = {}

        result = opa_engine._parse_opa_response(opa_response)

        assert result.allowed is False
        assert "No policy evaluation result" in result.reason

    @pytest.mark.asyncio
    async def test_evaluate_all_success(self, opa_engine, sample_check_request):
        """Test successful policy evaluation."""
        # Mock the OPA client
        mock_opa_response = {
            "result": {"allow": True, "reason": "User has read access"}
        }

        with patch.object(
            opa_engine.opa_client, "evaluate_policy", new_callable=AsyncMock
        ) as mock_evaluate:
            mock_evaluate.return_value = mock_opa_response

            result = await opa_engine.evaluate_all(sample_check_request)

            assert result.allowed is True
            assert result.reason == "User has read access"

            # Verify the input was prepared correctly
            mock_evaluate.assert_called_once_with(
                policy_path="eunomia/allow",
                input_data={
                    "principal": {
                        "uri": "user://john.doe",
                        "attributes": {"role": "user", "organization": "acme"},
                        "type": "principal",
                    },
                    "resource": {
                        "uri": "doc://sensitive",
                        "attributes": {
                            "type": "document",
                            "classification": "confidential",
                        },
                        "type": "resource",
                    },
                    "action": "read",
                },
            )

    @pytest.mark.asyncio
    async def test_evaluate_all_opa_exception(self, opa_engine, sample_check_request):
        """Test handling of OPA exceptions."""
        with patch.object(
            opa_engine.opa_client, "evaluate_policy", new_callable=AsyncMock
        ) as mock_evaluate:
            mock_evaluate.side_effect = OPAException("Connection failed")

            with pytest.raises(OPAException, match="Connection failed"):
                await opa_engine.evaluate_all(sample_check_request)

    def test_legacy_methods_warnings(self, opa_engine):
        """Test that legacy methods log warnings."""
        with patch("eunomia.engine.opa_engine.logger") as mock_logger:
            # Test add_policy
            opa_engine.add_policy(Mock())
            mock_logger.warning.assert_called()

            # Test remove_policy
            result = opa_engine.remove_policy("test")
            assert result is False

            # Test get_policies
            policies = opa_engine.get_policies()
            assert policies == []

            # Test get_policy
            policy = opa_engine.get_policy("test")
            assert policy is None

    @pytest.mark.asyncio
    async def test_close(self, opa_engine):
        """Test closing the engine."""
        with patch.object(
            opa_engine.opa_client, "close", new_callable=AsyncMock
        ) as mock_close:
            await opa_engine.close()
            mock_close.assert_called_once()
