import pytest
from eunomia_core import schemas
from pydantic import ValidationError


@pytest.fixture
def valid_attributes_list():
    return [{"key": "test", "value": "test"}]


@pytest.fixture
def valid_attributes_dict():
    return {"test": "test"}


class TestEntityRegisterRequest:
    def test_valid_cases(self, valid_attributes_list, valid_attributes_dict):
        # Both URI and attributes
        schemas.EntityCreate.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_list}
        )

        # Both URI and attributes (dict format)
        schemas.EntityCreate.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_dict}
        )

        # Attributes only (URI is optional)
        schemas.EntityCreate.model_validate(
            {"type": "resource", "attributes": valid_attributes_list}
        )

    def test_invalid_cases(self):
        # URI only (missing attributes)
        with pytest.raises(ValidationError):
            schemas.EntityCreate.model_validate(
                {
                    "type": "resource",
                    "uri": "123",
                }
            )

        # URI with empty attributes
        with pytest.raises(ValidationError):
            schemas.EntityCreate.model_validate(
                {
                    "type": "resource",
                    "uri": "123",
                    "attributes": [],
                }
            )

        # Neither URI nor attributes
        with pytest.raises(ValidationError):
            schemas.EntityCreate.model_validate({"type": "resource"})


class TestEntityUpdateRequest:
    def test_valid_cases(self, valid_attributes_list, valid_attributes_dict):
        # Both URI and attributes
        schemas.EntityUpdate.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_list}
        )

        # Both URI and attributes (dict format)
        schemas.EntityUpdate.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_dict}
        )

    def test_invalid_cases(self):
        # URI only (missing attributes)
        with pytest.raises(ValidationError):
            schemas.EntityUpdate.model_validate(
                {
                    "type": "resource",
                    "uri": "123",
                }
            )

        # URI with empty attributes
        with pytest.raises(ValidationError):
            schemas.EntityUpdate.model_validate(
                {
                    "type": "resource",
                    "uri": "123",
                    "attributes": [],
                }
            )

        # Attributes only (missing URI)
        with pytest.raises(ValidationError):
            schemas.EntityUpdate.model_validate(
                {
                    "type": "resource",
                    "attributes": [{"key": "test", "value": "test"}],
                }
            )

        # Neither URI nor attributes
        with pytest.raises(ValidationError):
            schemas.EntityUpdate.model_validate({"type": "resource"})


class TestEntityCheckRequest:
    def test_valid_cases(self, valid_attributes_list, valid_attributes_dict):
        # Both URI and attributes
        schemas.EntityAccess.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_list}
        )

        # Both URI and attributes (dict format)
        schemas.EntityAccess.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_dict}
        )

        # URI only
        schemas.EntityAccess.model_validate(
            {
                "type": "resource",
                "uri": "123",
            }
        )

        # URI with empty attributes
        schemas.EntityAccess.model_validate(
            {
                "type": "resource",
                "uri": "123",
                "attributes": [],
            }
        )

        # Attributes only
        schemas.EntityAccess.model_validate(
            {
                "type": "resource",
                "attributes": valid_attributes_list,
            }
        )

    def test_invalid_cases(self):
        # Empty attributes only
        with pytest.raises(ValidationError):
            schemas.EntityAccess.model_validate(
                {
                    "type": "resource",
                    "attributes": [],
                }
            )

        # Neither URI nor attributes
        with pytest.raises(ValidationError):
            schemas.EntityAccess.model_validate({"type": "resource"})


class TestResourceAccess:
    def test_valid_resource_type(self):
        # Valid when type is explicitly "resource"
        resource = schemas.ResourceAccess.model_validate(
            {"type": "resource", "uri": "123"}
        )
        assert resource.type.value == "resource"

    def test_type_override_from_any(self):
        # Type "any" should be overridden to "resource"
        resource = schemas.ResourceAccess.model_validate({"type": "any", "uri": "123"})
        assert resource.type.value == "resource"

    def test_invalid_type(self):
        # Should raise validation error for invalid type
        with pytest.raises(ValidationError):
            schemas.ResourceAccess.model_validate({"type": "principal", "uri": "123"})


class TestPrincipalAccess:
    def test_valid_principal_type(self):
        # Valid when type is explicitly "principal"
        principal = schemas.PrincipalAccess.model_validate(
            {"type": "principal", "uri": "123"}
        )
        assert principal.type.value == "principal"

    def test_type_override_from_any(self):
        # Type "any" should be overridden to "principal"
        principal = schemas.PrincipalAccess.model_validate(
            {"type": "any", "uri": "123"}
        )
        assert principal.type.value == "principal"

    def test_invalid_type(self):
        # Should raise validation error for invalid type
        with pytest.raises(ValidationError):
            schemas.PrincipalAccess.model_validate({"type": "resource", "uri": "123"})
