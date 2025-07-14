from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from jose import JWTError, jwt

from eunomia.fetchers.factory import FetcherFactory
from eunomia.fetchers.passport import PassportFetcher, PassportFetcherConfig
from eunomia.fetchers.passport.schemas import PassportJWT


class TestPassportFetcherConfig:
    """Test the PassportFetcherConfig class"""

    def test_default_config(self):
        """Test creating config with minimal required parameters"""
        config = PassportFetcherConfig(jwt_secret="test-secret")

        assert config.jwt_secret == "test-secret"
        assert config.jwt_algorithm == "HS256"
        assert config.jwt_issuer == "eunomia"
        assert config.jwt_default_ttl == 120 * 60  # 2 hours
        assert config.requires_registry is False

    def test_custom_config(self):
        """Test creating config with custom parameters"""
        config = PassportFetcherConfig(
            jwt_secret="custom-secret",
            jwt_algorithm="HS512",
            jwt_issuer="custom-issuer",
            jwt_default_ttl=3600,
            requires_registry=True,
        )

        assert config.jwt_secret == "custom-secret"
        assert config.jwt_algorithm == "HS512"
        assert config.jwt_issuer == "custom-issuer"
        assert config.jwt_default_ttl == 3600
        assert config.requires_registry is True


class TestPassportFetcher:
    """Test the PassportFetcher class functionality"""

    def test_init_basic_config(self, passport_fetcher, passport_config):
        """Test fetcher initialization with basic config"""
        assert passport_fetcher.config == passport_config
        assert passport_fetcher._registry is None

    def test_init_with_registry_config(self, passport_config_with_registry):
        """Test fetcher initialization with registry config"""
        fetcher = PassportFetcher(passport_config_with_registry)
        assert fetcher.config.requires_registry is True
        assert fetcher._registry is None

    @patch.object(FetcherFactory, "get_fetcher")
    def test_post_init_with_registry_success(
        self, mock_get_fetcher, passport_config_with_registry, mock_registry_fetcher
    ):
        """Test post_init successfully initializes registry"""
        mock_get_fetcher.return_value = mock_registry_fetcher

        fetcher = PassportFetcher(passport_config_with_registry)
        fetcher.post_init()

        assert fetcher._registry == mock_registry_fetcher
        mock_get_fetcher.assert_called_once_with("registry")

    @patch.object(FetcherFactory, "get_fetcher")
    def test_post_init_with_registry_failure(
        self, mock_get_fetcher, passport_config_with_registry
    ):
        """Test post_init raises error when registry is required but not available"""
        mock_get_fetcher.side_effect = ValueError("Registry not found")

        fetcher = PassportFetcher(passport_config_with_registry)

        with pytest.raises(
            ValueError,
            match="Passport requires registry but registry fetcher is not initialized",
        ):
            fetcher.post_init()

    def test_post_init_without_registry_requirement(self, passport_fetcher):
        """Test post_init does nothing when registry is not required"""
        passport_fetcher.post_init()
        assert passport_fetcher._registry is None

    def test_issue_passport_basic(
        self, passport_fetcher, sample_uri, sample_attributes
    ):
        """Test basic passport issuance"""
        token, passport_id, ttl = passport_fetcher.issue_passport(
            sample_uri, sample_attributes, 3600
        )

        assert isinstance(token, str)
        assert passport_id.startswith("psp_")
        assert len(passport_id) == 16  # "psp_" + 12 hex characters
        assert ttl == 3600

        # Verify token can be decoded
        decoded = jwt.decode(
            token,
            passport_fetcher.config.jwt_secret,
            algorithms=[passport_fetcher.config.jwt_algorithm],
            issuer=passport_fetcher.config.jwt_issuer,
        )

        assert decoded["sub"] == sample_uri
        assert decoded["jti"] == passport_id
        assert decoded["iss"] == passport_fetcher.config.jwt_issuer
        assert decoded["attr"] == sample_attributes

    def test_issue_passport_default_ttl(self, passport_fetcher, sample_uri):
        """Test passport issuance with default TTL"""
        token, passport_id, ttl = passport_fetcher.issue_passport(sample_uri)

        assert ttl == passport_fetcher.config.jwt_default_ttl

        decoded = jwt.decode(
            token,
            passport_fetcher.config.jwt_secret,
            algorithms=[passport_fetcher.config.jwt_algorithm],
            issuer=passport_fetcher.config.jwt_issuer,
        )

        # Check expiration time
        expected_exp = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        actual_exp = datetime.fromtimestamp(decoded["exp"], timezone.utc)
        time_diff = abs((expected_exp - actual_exp).total_seconds())
        assert time_diff < 2  # Allow 2 seconds tolerance

    def test_issue_passport_with_registry(
        self, passport_fetcher_with_registry, sample_uri, sample_attributes
    ):
        """Test passport issuance with registry fetcher"""
        token, passport_id, ttl = passport_fetcher_with_registry.issue_passport(
            sample_uri, sample_attributes
        )

        # Verify registry was called
        passport_fetcher_with_registry._registry.get_entity.assert_called_once_with(
            sample_uri
        )

        # Verify token contains merged attributes
        decoded = jwt.decode(
            token,
            passport_fetcher_with_registry.config.jwt_secret,
            algorithms=[passport_fetcher_with_registry.config.jwt_algorithm],
            issuer=passport_fetcher_with_registry.config.jwt_issuer,
        )

        expected_attributes = {
            **sample_attributes,
            **{"name": "Test Resource", "type": "document", "owner": "user123"},
        }
        assert decoded["attr"] == expected_attributes

    def test_issue_passport_registry_entity_not_found(
        self, passport_fetcher_with_registry, sample_uri
    ):
        """Test passport issuance fails when entity not found in registry"""
        passport_fetcher_with_registry._registry.get_entity.return_value = None

        with pytest.raises(
            ValueError, match="Passport cannot be issued for non-registered entity"
        ):
            passport_fetcher_with_registry.issue_passport(sample_uri)

    @patch("uuid.uuid4")
    def test_issue_passport_deterministic_id(
        self, mock_uuid, passport_fetcher, sample_uri
    ):
        """Test passport ID generation is consistent"""
        mock_uuid.return_value.hex = "abcdef123456789012345678"

        token, passport_id, ttl = passport_fetcher.issue_passport(sample_uri)

        assert passport_id == "psp_abcdef123456"

    @patch("eunomia.fetchers.passport.main.logger")
    def test_issue_passport_logging_success(
        self, mock_logger, passport_fetcher, sample_uri
    ):
        """Test successful passport issuance is logged"""
        token, passport_id, ttl = passport_fetcher.issue_passport(sample_uri)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert "Passport issuance SUCCESS" in call_args[0][0]
        assert sample_uri in call_args[0][0]
        assert passport_id in call_args[0][0]

    @patch("eunomia.fetchers.passport.main.logger")
    def test_issue_passport_logging_failure(
        self, mock_logger, passport_fetcher_with_registry, sample_uri
    ):
        """Test failed passport issuance is logged"""
        passport_fetcher_with_registry._registry.get_entity.return_value = None

        with pytest.raises(ValueError):
            passport_fetcher_with_registry.issue_passport(sample_uri)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert "Passport issuance FAILURE" in call_args[0][0]
        assert sample_uri in call_args[0][0]

    def test_verify_passport_valid(
        self, passport_fetcher, valid_jwt_token, valid_passport_jwt
    ):
        """Test successful passport verification"""
        result = passport_fetcher._verify_passport(valid_jwt_token)

        assert isinstance(result, PassportJWT)
        assert result.jti == valid_passport_jwt.jti
        assert result.sub == valid_passport_jwt.sub
        assert result.iss == valid_passport_jwt.iss
        assert result.attr == valid_passport_jwt.attr

    def test_verify_passport_expired(self, passport_fetcher, expired_jwt_token):
        """Test passport verification fails for expired token"""
        with pytest.raises(JWTError):
            passport_fetcher._verify_passport(expired_jwt_token)

    def test_verify_passport_invalid_token(self, passport_fetcher, invalid_jwt_token):
        """Test passport verification fails for invalid token"""
        with pytest.raises(JWTError):
            passport_fetcher._verify_passport(invalid_jwt_token)

    def test_verify_passport_wrong_secret(self, passport_config, valid_passport_jwt):
        """Test passport verification fails with wrong secret"""
        # Create token with different secret
        wrong_token = jwt.encode(
            valid_passport_jwt.model_dump(),
            "wrong-secret",
            algorithm=passport_config.jwt_algorithm,
        )

        fetcher = PassportFetcher(passport_config)

        with pytest.raises(JWTError):
            fetcher._verify_passport(wrong_token)

    def test_verify_passport_wrong_issuer(self, passport_config, valid_passport_jwt):
        """Test passport verification fails with wrong issuer"""
        # Modify issuer
        jwt_data = valid_passport_jwt.model_dump()
        jwt_data["iss"] = "wrong-issuer"

        wrong_token = jwt.encode(
            jwt_data,
            passport_config.jwt_secret,
            algorithm=passport_config.jwt_algorithm,
        )

        fetcher = PassportFetcher(passport_config)

        with pytest.raises(JWTError):
            fetcher._verify_passport(wrong_token)

    @pytest.mark.asyncio
    async def test_fetch_attributes_valid_token(
        self, passport_fetcher, valid_jwt_token, valid_passport_jwt
    ):
        """Test fetching attributes with valid token"""
        attributes = await passport_fetcher.fetch_attributes(valid_jwt_token)

        expected_attributes = {**valid_passport_jwt.attr, "uri": valid_passport_jwt.sub}
        assert attributes == expected_attributes

    @pytest.mark.asyncio
    async def test_fetch_attributes_invalid_token(
        self, passport_fetcher, invalid_jwt_token
    ):
        """Test fetching attributes with invalid token raises error"""
        with pytest.raises(JWTError):
            await passport_fetcher.fetch_attributes(invalid_jwt_token)

    @pytest.mark.asyncio
    async def test_fetch_attributes_expired_token(
        self, passport_fetcher, expired_jwt_token
    ):
        """Test fetching attributes with expired token raises error"""
        with pytest.raises(JWTError):
            await passport_fetcher.fetch_attributes(expired_jwt_token)

    @pytest.mark.asyncio
    async def test_fetch_attributes_empty_attributes(
        self, passport_fetcher, passport_config
    ):
        """Test fetching attributes with empty attr field"""
        now = datetime.now(timezone.utc)
        jwt_payload = PassportJWT(
            jti="psp_test123456789",
            iat=int(now.timestamp()),
            exp=int((now + timedelta(seconds=3600)).timestamp()),
            iss=passport_config.jwt_issuer,
            sub="test://resource/1",
            attr={},
        )

        token = jwt.encode(
            jwt_payload.model_dump(),
            passport_config.jwt_secret,
            algorithm=passport_config.jwt_algorithm,
        )

        attributes = await passport_fetcher.fetch_attributes(token)

        expected_attributes = {"uri": "test://resource/1"}
        assert attributes == expected_attributes

    def test_integration_issue_and_verify(
        self, passport_fetcher, sample_uri, sample_attributes
    ):
        """Test complete integration: issue passport and then verify it"""
        # Issue passport
        token, passport_id, ttl = passport_fetcher.issue_passport(
            sample_uri, sample_attributes, 3600
        )

        # Verify the issued passport
        verified = passport_fetcher._verify_passport(token)

        assert verified.jti == passport_id
        assert verified.sub == sample_uri
        assert verified.attr == sample_attributes
        assert verified.iss == passport_fetcher.config.jwt_issuer

    @pytest.mark.asyncio
    async def test_integration_issue_and_fetch_attributes(
        self, passport_fetcher, sample_uri, sample_attributes
    ):
        """Test complete integration: issue passport and then fetch attributes"""
        # Issue passport
        token, passport_id, ttl = passport_fetcher.issue_passport(
            sample_uri, sample_attributes, 3600
        )

        # Fetch attributes using the token
        attributes = await passport_fetcher.fetch_attributes(token)

        expected_attributes = {**sample_attributes, "uri": sample_uri}
        assert attributes == expected_attributes

    def test_passport_expiration_timing(self, passport_fetcher, sample_uri):
        """Test that passport expiration is set correctly"""
        ttl = 1800  # 30 minutes
        before_issue = datetime.now(timezone.utc)

        token, passport_id, returned_ttl = passport_fetcher.issue_passport(
            sample_uri, {}, ttl
        )

        decoded = jwt.decode(
            token,
            passport_fetcher.config.jwt_secret,
            algorithms=[passport_fetcher.config.jwt_algorithm],
            issuer=passport_fetcher.config.jwt_issuer,
        )

        # Check that expiration is approximately correct (allow for some tolerance)
        expected_exp = before_issue + timedelta(seconds=ttl)
        actual_exp = datetime.fromtimestamp(decoded["exp"], timezone.utc)
        time_diff = abs((expected_exp - actual_exp).total_seconds())

        # Allow up to 2 seconds tolerance for timing differences
        assert time_diff <= 2, (
            f"Expected expiration around {expected_exp}, got {actual_exp} (diff: {time_diff}s)"
        )
        assert returned_ttl == ttl

    def test_multiple_passports_unique_ids(self, passport_fetcher, sample_uri):
        """Test that multiple passports have unique IDs"""
        token1, id1, _ = passport_fetcher.issue_passport(sample_uri)
        token2, id2, _ = passport_fetcher.issue_passport(sample_uri)
        token3, id3, _ = passport_fetcher.issue_passport(sample_uri)

        assert id1 != id2 != id3
        assert all(id.startswith("psp_") for id in [id1, id2, id3])
        assert all(len(id) == 16 for id in [id1, id2, id3])

    def test_passport_with_complex_attributes(self, passport_fetcher, sample_uri):
        """Test passport issuance with complex attribute types"""
        complex_attributes = {
            "string_attr": "test",
            "number_attr": 42,
            "float_attr": 3.14,
            "bool_attr": True,
            "list_attr": [1, 2, 3, "test"],
            "dict_attr": {"nested": {"key": "value"}},
            "null_attr": None,
        }

        token, passport_id, ttl = passport_fetcher.issue_passport(
            sample_uri, complex_attributes
        )

        # Verify all attribute types are preserved
        verified = passport_fetcher._verify_passport(token)
        assert verified.attr == complex_attributes
