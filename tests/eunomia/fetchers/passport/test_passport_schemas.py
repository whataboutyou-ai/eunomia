from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from eunomia.fetchers.passport.schemas import (
    PassportIssueRequest,
    PassportIssueResponse,
    PassportJWT,
)


class TestPassportJWT:
    """Test the PassportJWT schema"""

    def test_valid_passport_jwt(self):
        """Test creating a valid PassportJWT"""
        now = datetime.now(timezone.utc)
        passport = PassportJWT(
            jti="psp_test123456789",
            iat=int(now.timestamp()),
            exp=int((now + timedelta(hours=2)).timestamp()),
            iss="eunomia",
            sub="test://resource/1",
            attr={"name": "Test Resource", "type": "document"},
        )

        assert passport.jti == "psp_test123456789"
        assert passport.iss == "eunomia"
        assert passport.sub == "test://resource/1"
        assert passport.attr == {"name": "Test Resource", "type": "document"}

    def test_passport_jwt_default_attr(self):
        """Test PassportJWT with default empty attributes"""
        now = datetime.now(timezone.utc)
        passport = PassportJWT(
            jti="psp_test123456789",
            iat=int(now.timestamp()),
            exp=int((now + timedelta(hours=2)).timestamp()),
            iss="eunomia",
            sub="test://resource/1",
        )

        assert passport.attr == {}

    def test_passport_jwt_complex_attributes(self):
        """Test PassportJWT with complex attribute types"""
        now = datetime.now(timezone.utc)
        complex_attr = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": {"key": "value"}},
            "null": None,
        }

        passport = PassportJWT(
            jti="psp_test123456789",
            iat=int(now.timestamp()),
            exp=int((now + timedelta(hours=2)).timestamp()),
            iss="eunomia",
            sub="test://resource/1",
            attr=complex_attr,
        )

        assert passport.attr == complex_attr

    def test_passport_jwt_required_fields(self):
        """Test that all required fields must be provided"""
        with pytest.raises(ValidationError):
            PassportJWT()

    def test_passport_jwt_missing_jti(self):
        """Test PassportJWT missing jti field"""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError) as exc_info:
            PassportJWT(
                iat=int(now.timestamp()),
                exp=int((now + timedelta(hours=2)).timestamp()),
                iss="eunomia",
                sub="test://resource/1",
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("jti",) and error["type"] == "missing" for error in errors
        )

    def test_passport_jwt_missing_sub(self):
        """Test PassportJWT missing sub field"""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError) as exc_info:
            PassportJWT(
                jti="psp_test123456789",
                iat=int(now.timestamp()),
                exp=int((now + timedelta(hours=2)).timestamp()),
                iss="eunomia",
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("sub",) and error["type"] == "missing" for error in errors
        )

    def test_passport_jwt_serialization(self):
        """Test PassportJWT model serialization"""
        now = datetime.now(timezone.utc)
        passport = PassportJWT(
            jti="psp_test123456789",
            iat=int(now.timestamp()),
            exp=int((now + timedelta(hours=2)).timestamp()),
            iss="eunomia",
            sub="test://resource/1",
            attr={"name": "Test Resource"},
        )

        dumped = passport.model_dump()

        assert dumped["jti"] == "psp_test123456789"
        assert dumped["iss"] == "eunomia"
        assert dumped["sub"] == "test://resource/1"
        assert dumped["attr"] == {"name": "Test Resource"}
        assert "iat" in dumped
        assert "exp" in dumped


class TestPassportIssueRequest:
    """Test the PassportIssueRequest schema"""

    def test_valid_issue_request(self):
        """Test creating a valid PassportIssueRequest"""
        request = PassportIssueRequest(
            uri="test://resource/1",
            attributes={"name": "Test Resource", "type": "document"},
            ttl=3600,
        )

        assert request.uri == "test://resource/1"
        assert request.attributes == {"name": "Test Resource", "type": "document"}
        assert request.ttl == 3600

    def test_issue_request_default_attributes(self):
        """Test PassportIssueRequest with default empty attributes"""
        request = PassportIssueRequest(uri="test://resource/1")

        assert request.uri == "test://resource/1"
        assert request.attributes == {}
        assert request.ttl is None

    def test_issue_request_default_ttl(self):
        """Test PassportIssueRequest with default None ttl"""
        request = PassportIssueRequest(
            uri="test://resource/1", attributes={"name": "Test Resource"}
        )

        assert request.ttl is None

    def test_issue_request_required_uri(self):
        """Test that uri is required for PassportIssueRequest"""
        with pytest.raises(ValidationError) as exc_info:
            PassportIssueRequest()

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("uri",) and error["type"] == "missing" for error in errors
        )

    def test_issue_request_empty_uri(self):
        """Test PassportIssueRequest with empty uri"""
        request = PassportIssueRequest(uri="")

        assert request.uri == ""

    def test_issue_request_complex_attributes(self):
        """Test PassportIssueRequest with complex attributes"""
        complex_attr = {
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        request = PassportIssueRequest(
            uri="test://resource/1", attributes=complex_attr, ttl=7200
        )

        assert request.attributes == complex_attr

    def test_issue_request_serialization(self):
        """Test PassportIssueRequest model serialization"""
        request = PassportIssueRequest(
            uri="test://resource/1", attributes={"name": "Test Resource"}, ttl=3600
        )

        dumped = request.model_dump()

        assert dumped["uri"] == "test://resource/1"
        assert dumped["attributes"] == {"name": "Test Resource"}
        assert dumped["ttl"] == 3600


class TestPassportIssueResponse:
    """Test the PassportIssueResponse schema"""

    def test_valid_issue_response(self):
        """Test creating a valid PassportIssueResponse"""
        response = PassportIssueResponse(
            passport="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            passport_id="psp_test123456789",
            expires_in=3600,
        )

        assert response.passport.startswith("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        assert response.passport_id == "psp_test123456789"
        assert response.expires_in == 3600

    def test_issue_response_required_fields(self):
        """Test that all fields are required for PassportIssueResponse"""
        with pytest.raises(ValidationError):
            PassportIssueResponse()

    def test_issue_response_missing_passport(self):
        """Test PassportIssueResponse missing passport field"""
        with pytest.raises(ValidationError) as exc_info:
            PassportIssueResponse(passport_id="psp_test123456789", expires_in=3600)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("passport",) and error["type"] == "missing"
            for error in errors
        )

    def test_issue_response_missing_passport_id(self):
        """Test PassportIssueResponse missing passport_id field"""
        with pytest.raises(ValidationError) as exc_info:
            PassportIssueResponse(
                passport="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", expires_in=3600
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("passport_id",) and error["type"] == "missing"
            for error in errors
        )

    def test_issue_response_missing_expires_in(self):
        """Test PassportIssueResponse missing expires_in field"""
        with pytest.raises(ValidationError) as exc_info:
            PassportIssueResponse(
                passport="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                passport_id="psp_test123456789",
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("expires_in",) and error["type"] == "missing"
            for error in errors
        )

    def test_issue_response_empty_strings(self):
        """Test PassportIssueResponse with empty strings"""
        response = PassportIssueResponse(passport="", passport_id="", expires_in=0)

        assert response.passport == ""
        assert response.passport_id == ""
        assert response.expires_in == 0

    def test_issue_response_serialization(self):
        """Test PassportIssueResponse model serialization"""
        response = PassportIssueResponse(
            passport="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            passport_id="psp_test123456789",
            expires_in=3600,
        )

        dumped = response.model_dump()

        assert dumped["passport"] == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert dumped["passport_id"] == "psp_test123456789"
        assert dumped["expires_in"] == 3600

    def test_all_schemas_json_compatibility(self):
        """Test that all schemas can be serialized to and from JSON"""
        import json

        # Test PassportJWT
        now = datetime.now(timezone.utc)
        passport_jwt = PassportJWT(
            jti="psp_test123456789",
            iat=int(now.timestamp()),
            exp=int((now + timedelta(hours=2)).timestamp()),
            iss="eunomia",
            sub="test://resource/1",
            attr={"name": "Test Resource"},
        )

        passport_json = json.dumps(passport_jwt.model_dump())
        passport_data = json.loads(passport_json)
        restored_passport = PassportJWT.model_validate(passport_data)
        assert restored_passport == passport_jwt

        # Test PassportIssueRequest
        issue_request = PassportIssueRequest(
            uri="test://resource/1", attributes={"name": "Test Resource"}, ttl=3600
        )

        request_json = json.dumps(issue_request.model_dump())
        request_data = json.loads(request_json)
        restored_request = PassportIssueRequest.model_validate(request_data)
        assert restored_request == issue_request

        # Test PassportIssueResponse
        issue_response = PassportIssueResponse(
            passport="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            passport_id="psp_test123456789",
            expires_in=3600,
        )

        response_json = json.dumps(issue_response.model_dump())
        response_data = json.loads(response_json)
        restored_response = PassportIssueResponse.model_validate(response_data)
        assert restored_response == issue_response
