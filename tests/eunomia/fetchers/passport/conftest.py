from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from eunomia_core import enums
from jose import jwt

from eunomia.fetchers.passport import PassportFetcher, PassportFetcherConfig
from eunomia.fetchers.passport.schemas import PassportIssueRequest, PassportJWT
from eunomia.fetchers.registry import RegistryFetcher


@pytest.fixture
def passport_config():
    """Create a basic passport fetcher configuration for testing."""
    return PassportFetcherConfig(
        jwt_secret="test-secret-key-for-testing",
        jwt_algorithm="HS256",
        jwt_issuer="eunomia-test",
        jwt_default_ttl=7200,  # 2 hours
        requires_registry=False,
    )


@pytest.fixture
def passport_config_with_registry():
    """Create a passport fetcher configuration that requires registry."""
    return PassportFetcherConfig(
        jwt_secret="test-secret-key-for-testing",
        jwt_algorithm="HS256",
        jwt_issuer="eunomia-test",
        jwt_default_ttl=7200,
        requires_registry=True,
    )


@pytest.fixture
def passport_fetcher(passport_config):
    """Create a passport fetcher instance for testing."""
    return PassportFetcher(passport_config)


@pytest.fixture
def mock_registry_fetcher():
    """Create a mock registry fetcher for testing."""
    mock_registry = Mock(spec=RegistryFetcher)

    # Mock entity for testing
    mock_entity = Mock()
    mock_entity.uri = "test://resource/1"
    mock_entity.type = enums.EntityType.resource
    mock_entity.attributes_dict = {
        "name": "Test Resource",
        "type": "document",
        "owner": "user123",
    }

    mock_registry.get_entity.return_value = mock_entity
    return mock_registry


@pytest.fixture
def passport_fetcher_with_registry(
    passport_config_with_registry, mock_registry_fetcher
):
    """Create a passport fetcher instance with mocked registry."""
    fetcher = PassportFetcher(passport_config_with_registry)
    fetcher._registry = mock_registry_fetcher
    return fetcher


@pytest.fixture
def sample_uri():
    """Sample URI for testing."""
    return "test://resource/1"


@pytest.fixture
def sample_attributes():
    """Sample attributes for testing."""
    return {
        "name": "Test Resource",
        "type": "document",
        "owner": "user123",
        "tags": ["public", "test"],
    }


@pytest.fixture
def valid_passport_jwt():
    """Create a valid passport JWT payload for testing."""
    now = datetime.now(timezone.utc)
    return PassportJWT(
        jti="psp_test123456789",
        iat=int(now.timestamp()),
        exp=int((now + timedelta(seconds=7200)).timestamp()),
        iss="eunomia-test",
        sub="test://resource/1",
        attr={"name": "Test Resource", "type": "document", "owner": "user123"},
    )


@pytest.fixture
def expired_passport_jwt():
    """Create an expired passport JWT payload for testing."""
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    return PassportJWT(
        jti="psp_expired123456",
        iat=int((past_time - timedelta(seconds=7200)).timestamp()),
        exp=int(past_time.timestamp()),
        iss="eunomia-test",
        sub="test://resource/1",
        attr={"name": "Test Resource"},
    )


@pytest.fixture
def valid_jwt_token(passport_config, valid_passport_jwt):
    """Create a valid JWT token string for testing."""
    return jwt.encode(
        valid_passport_jwt.model_dump(),
        passport_config.jwt_secret,
        algorithm=passport_config.jwt_algorithm,
    )


@pytest.fixture
def expired_jwt_token(passport_config, expired_passport_jwt):
    """Create an expired JWT token string for testing."""
    return jwt.encode(
        expired_passport_jwt.model_dump(),
        passport_config.jwt_secret,
        algorithm=passport_config.jwt_algorithm,
    )


@pytest.fixture
def invalid_jwt_token():
    """Create an invalid JWT token string for testing."""
    return "invalid.jwt.token"


@pytest.fixture
def passport_issue_request():
    """Create a sample passport issue request for testing."""
    return PassportIssueRequest(
        uri="test://resource/1",
        attributes={"name": "Test Resource", "type": "document"},
        ttl=3600,
    )
