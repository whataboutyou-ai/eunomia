import pytest


@pytest.fixture
def valid_attributes_list():
    return [{"key": "test", "value": "test"}]


@pytest.fixture
def valid_attributes_dict():
    return {"test": "test"}
