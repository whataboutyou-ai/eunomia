import pytest
from eunomia_core import schemas
from pydantic import ValidationError


@pytest.fixture
def valid_attributes_list():
    return [{"key": "test", "value": "test"}]


@pytest.fixture
def valid_attributes_dict():
    return {"test": "test"}


class TestEntityCreate:
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
        entity = schemas.EntityCreate.model_validate(
            {"type": "resource", "attributes": valid_attributes_list}
        )
        assert entity.uri is not None

        # Attributes and None URI
        entity = schemas.EntityCreate.model_validate(
            {"type": "resource", "uri": None, "attributes": valid_attributes_list}
        )
        assert entity.uri is not None

    def test_invalid_cases(self, valid_attributes_list):
        # Both URI and attributes with duplicate keys
        with pytest.raises(ValidationError):
            schemas.EntityCreate.model_validate(
                {
                    "type": "resource",
                    "uri": "123",
                    "attributes": valid_attributes_list + valid_attributes_list,
                }
            )

        # URI only (missing attributes)
        with pytest.raises(ValidationError):
            schemas.EntityCreate.model_validate({"type": "resource", "uri": "123"})

        # URI with empty attributes
        with pytest.raises(ValidationError):
            schemas.EntityCreate.model_validate(
                {"type": "resource", "uri": "123", "attributes": []}
            )

        # Neither URI nor attributes
        with pytest.raises(ValidationError):
            schemas.EntityCreate.model_validate({"type": "resource"})


class TestEntityUpdate:
    def test_valid_cases(self, valid_attributes_list, valid_attributes_dict):
        # Both URI and attributes
        schemas.EntityUpdate.model_validate(
            {"uri": "123", "attributes": valid_attributes_list}
        )

        # Both URI and attributes (dict format)
        schemas.EntityUpdate.model_validate(
            {"uri": "123", "attributes": valid_attributes_dict}
        )

    def test_invalid_cases(self):
        # URI only (missing attributes)
        with pytest.raises(ValidationError):
            schemas.EntityUpdate.model_validate({"uri": "123"})

        # URI with empty attributes
        with pytest.raises(ValidationError):
            schemas.EntityUpdate.model_validate({"uri": "123", "attributes": []})

        # Attributes only (missing URI)
        with pytest.raises(ValidationError):
            schemas.EntityUpdate.model_validate(
                {"attributes": [{"key": "test", "value": "test"}]}
            )

        # Neither URI nor attributes
        with pytest.raises(ValidationError):
            schemas.EntityUpdate.model_validate({})


class TestEntityAccess:
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
        schemas.EntityAccess.model_validate({"type": "resource", "uri": "123"})

        # URI with empty attributes
        schemas.EntityAccess.model_validate(
            {"type": "resource", "uri": "123", "attributes": []}
        )

        # Attributes only
        schemas.EntityAccess.model_validate(
            {"type": "resource", "attributes": valid_attributes_list}
        )

    def test_invalid_cases(self, valid_attributes_list):
        # Attributes with duplicate keys
        with pytest.raises(ValidationError):
            schemas.EntityAccess.model_validate(
                {"attributes": valid_attributes_list + valid_attributes_list}
            )

        # Empty attributes only
        with pytest.raises(ValidationError):
            schemas.EntityAccess.model_validate({"type": "resource", "attributes": []})

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

    def test_invalid_type(self):
        # Should raise validation error for invalid type
        with pytest.raises(ValidationError):
            schemas.PrincipalAccess.model_validate({"type": "resource", "uri": "123"})
