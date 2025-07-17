import pytest
from eunomia_core.schemas.entity import EntityCreate, EntityUpdate
from pydantic import ValidationError


class TestEntityCreate:
    def test_valid_cases(self, valid_attributes_list, valid_attributes_dict):
        # Both URI and attributes
        EntityCreate.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_list}
        )

        # Both URI and attributes (dict format)
        EntityCreate.model_validate(
            {"type": "resource", "uri": "123", "attributes": valid_attributes_dict}
        )

        # Attributes only (URI is optional)
        entity = EntityCreate.model_validate(
            {"type": "resource", "attributes": valid_attributes_list}
        )
        assert entity.uri is not None

        # Attributes and None URI
        entity = EntityCreate.model_validate(
            {"type": "resource", "uri": None, "attributes": valid_attributes_list}
        )
        assert entity.uri is not None

    def test_invalid_cases(self, valid_attributes_list):
        # Both URI and attributes with duplicate keys
        with pytest.raises(ValidationError):
            EntityCreate.model_validate(
                {
                    "type": "resource",
                    "uri": "123",
                    "attributes": valid_attributes_list + valid_attributes_list,
                }
            )

        # URI only (missing attributes)
        with pytest.raises(ValidationError):
            EntityCreate.model_validate({"type": "resource", "uri": "123"})

        # URI with empty attributes
        with pytest.raises(ValidationError):
            EntityCreate.model_validate(
                {"type": "resource", "uri": "123", "attributes": []}
            )

        # Neither URI nor attributes
        with pytest.raises(ValidationError):
            EntityCreate.model_validate({"type": "resource"})


class TestEntityUpdate:
    def test_valid_cases(self, valid_attributes_list, valid_attributes_dict):
        # Both URI and attributes
        EntityUpdate.model_validate({"uri": "123", "attributes": valid_attributes_list})

        # Both URI and attributes (dict format)
        EntityUpdate.model_validate({"uri": "123", "attributes": valid_attributes_dict})

    def test_invalid_cases(self):
        # URI only (missing attributes)
        with pytest.raises(ValidationError):
            EntityUpdate.model_validate({"uri": "123"})

        # URI with empty attributes
        with pytest.raises(ValidationError):
            EntityUpdate.model_validate({"uri": "123", "attributes": []})

        # Attributes only (missing URI)
        with pytest.raises(ValidationError):
            EntityUpdate.model_validate(
                {"attributes": [{"key": "test", "value": "test"}]}
            )

        # Neither URI nor attributes
        with pytest.raises(ValidationError):
            EntityUpdate.model_validate({})
