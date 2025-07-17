import pytest
from eunomia_core.schemas.check import (
    CheckRequest,
    CheckResponse,
    EntityCheck,
    PrincipalCheck,
    ResourceCheck,
)
from pydantic import ValidationError


class TestEntityCheck:
    def test_valid_cases(self, valid_attributes_list, valid_attributes_dict):
        # Both URI and attributes
        EntityCheck.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_list}
        )

        # Both URI and attributes (dict format)
        EntityCheck.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_dict}
        )

        # URI only
        EntityCheck.model_validate({"type": "resource", "uri": "123"})

        # URI with empty attributes
        EntityCheck.model_validate({"type": "resource", "uri": "123", "attributes": []})

        # Attributes only
        EntityCheck.model_validate(
            {"type": "resource", "attributes": valid_attributes_list}
        )

    def test_invalid_cases(self, valid_attributes_list):
        # Attributes with duplicate keys
        with pytest.raises(ValidationError):
            EntityCheck.model_validate(
                {"attributes": valid_attributes_list + valid_attributes_list}
            )

        # Empty attributes only
        with pytest.raises(ValidationError):
            EntityCheck.model_validate({"type": "resource", "attributes": []})

        # Neither URI nor attributes
        with pytest.raises(ValidationError):
            EntityCheck.model_validate({"type": "resource"})


class TestResourceCheck:
    def test_valid_resource_type(self):
        # Valid when type is explicitly "resource"
        resource = ResourceCheck.model_validate({"type": "resource", "uri": "123"})
        assert resource.type.value == "resource"

    def test_invalid_type(self):
        # Should raise validation error for invalid type
        with pytest.raises(ValidationError):
            ResourceCheck.model_validate({"type": "principal", "uri": "123"})


class TestPrincipalCheck:
    def test_valid_principal_type(self):
        # Valid when type is explicitly "principal"
        principal = PrincipalCheck.model_validate({"type": "principal", "uri": "123"})
        assert principal.type.value == "principal"

    def test_invalid_type(self):
        # Should raise validation error for invalid type
        with pytest.raises(ValidationError):
            PrincipalCheck.model_validate({"type": "resource", "uri": "123"})


class TestCheckRequest:
    def test_valid_cases(self):
        # Valid request with all required fields
        request = CheckRequest.model_validate(
            {
                "principal": {"type": "principal", "uri": "user:123"},
                "resource": {"type": "resource", "uri": "file:456"},
                "action": "read",
            }
        )
        assert request.principal.type.value == "principal"
        assert request.resource.type.value == "resource"
        assert request.action == "read"

        # Valid request with default action
        request = CheckRequest.model_validate(
            {
                "principal": {"type": "principal", "uri": "user:123"},
                "resource": {"type": "resource", "uri": "file:456"},
            }
        )
        assert request.action == "access"

        # Valid request with attributes instead of URIs
        request = CheckRequest.model_validate(
            {
                "principal": {
                    "type": "principal",
                    "attributes": {"name": "john", "role": "admin"},
                },
                "resource": {
                    "type": "resource",
                    "attributes": {"path": "/data", "owner": "system"},
                },
                "action": "write",
            }
        )
        assert request.principal.attributes == {"name": "john", "role": "admin"}
        assert request.resource.attributes == {"path": "/data", "owner": "system"}

    def test_invalid_cases(self):
        # Missing principal
        with pytest.raises(ValidationError):
            CheckRequest.model_validate(
                {"resource": {"type": "resource", "uri": "file:456"}, "action": "read"}
            )

        # Missing resource
        with pytest.raises(ValidationError):
            CheckRequest.model_validate(
                {
                    "principal": {"type": "principal", "uri": "user:123"},
                    "action": "read",
                }
            )

        # Invalid principal type
        with pytest.raises(ValidationError):
            CheckRequest.model_validate(
                {
                    "principal": {"type": "resource", "uri": "user:123"},
                    "resource": {"type": "resource", "uri": "file:456"},
                }
            )

        # Invalid resource type
        with pytest.raises(ValidationError):
            CheckRequest.model_validate(
                {
                    "principal": {"type": "principal", "uri": "user:123"},
                    "resource": {"type": "principal", "uri": "file:456"},
                }
            )

        # Principal with neither URI nor attributes
        with pytest.raises(ValidationError):
            CheckRequest.model_validate(
                {
                    "principal": {"type": "principal"},
                    "resource": {"type": "resource", "uri": "file:456"},
                }
            )

        # Resource with neither URI nor attributes
        with pytest.raises(ValidationError):
            CheckRequest.model_validate(
                {
                    "principal": {"type": "principal", "uri": "user:123"},
                    "resource": {"type": "resource"},
                }
            )


class TestCheckResponse:
    def test_valid_cases(self):
        # Valid response with allowed=True and reason
        response = CheckResponse.model_validate(
            {"allowed": True, "reason": "User has admin privileges"}
        )
        assert response.allowed is True
        assert response.reason == "User has admin privileges"

        # Valid response with allowed=False and reason
        response = CheckResponse.model_validate(
            {"allowed": False, "reason": "Insufficient permissions"}
        )
        assert response.allowed is False
        assert response.reason == "Insufficient permissions"

        # Valid response without reason
        response = CheckResponse.model_validate({"allowed": True})
        assert response.allowed is True
        assert response.reason is None

        # Valid response with None reason
        response = CheckResponse.model_validate({"allowed": False, "reason": None})
        assert response.allowed is False
        assert response.reason is None

    def test_invalid_cases(self):
        # Missing allowed field
        with pytest.raises(ValidationError):
            CheckResponse.model_validate({"reason": "Some reason"})

        # Invalid allowed type
        with pytest.raises(ValidationError):
            CheckResponse.model_validate({"allowed": "invalid"})

        # Empty dict
        with pytest.raises(ValidationError):
            CheckResponse.model_validate({})
