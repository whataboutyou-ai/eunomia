import re
import uuid

from eunomia_core.utils import generate_uri, slugify


class TestSlugify:
    """Test cases for the slugify function."""

    def test_emoji_removal(self):
        """Test that emojis are properly removed."""
        assert slugify("Planetary Weather 🪐") == "planetary-weather"

    def test_special_characters(self):
        """Test that special characters are replaced with hyphens."""
        assert slugify("some/strange?stuff") == "some-strange-stuff"

    def test_leading_trailing_spaces(self):
        """Test that leading and trailing spaces are stripped."""
        assert slugify("  Hello World!  ") == "hello-world"

    def test_mixed_separators(self):
        """Test various separators (underscores, dots, spaces) are normalized."""
        assert slugify("My_Awesome-Project v1.0") == "my_awesome-project-v1-0"

    def test_plus_signs(self):
        """Test that plus signs are handled correctly."""
        assert slugify("C++ Programming Guide") == "c-programming-guide"

    def test_ampersand_and_symbols(self):
        """Test ampersands and other symbols are replaced."""
        assert (
            slugify("Another Test String with Spaces & Symbols!")
            == "another-test-string-with-spaces-symbols"
        )

    def test_numbers_preserved(self):
        """Test that numbers are preserved in the slug."""
        assert slugify("123 ABC def") == "123-abc-def"

    def test_multiple_hyphens(self):
        """Test that multiple consecutive hyphens are collapsed and trimmed."""
        assert slugify("---leading-and-trailing---") == "leading-and-trailing"

    def test_no_special_characters(self):
        """Test strings with no special characters are just lowercased."""
        assert slugify("NoSpecialCharactersHere") == "nospecialcharactershere"

    def test_spaces_normalization(self):
        """Test that internal and external spaces are handled correctly."""
        assert (
            slugify("  leading and trailing spaces  ") == "leading-and-trailing-spaces"
        )

    def test_unicode_normalization(self):
        """Test that accented characters are normalized to ASCII."""
        assert slugify("München Hauptbahnhof") == "munchen-hauptbahnhof"

    def test_non_ascii_removal(self):
        """Test that non-ASCII characters that can't be normalized are removed."""
        assert slugify("你好世界") == ""

    def test_empty_string(self):
        """Test empty string input."""
        assert slugify("") == ""

    def test_only_spaces(self):
        """Test string with only spaces."""
        assert slugify("   ") == ""

    def test_only_special_characters(self):
        """Test string with only special characters."""
        assert slugify("!@#$%^&*()") == ""

    def test_single_character(self):
        """Test single character inputs."""
        assert slugify("A") == "a"
        assert slugify("1") == "1"
        assert slugify("-") == ""

    def test_hyphen_preservation(self):
        """Test that existing hyphens are preserved (not duplicated)."""
        assert slugify("already-hyphenated-string") == "already-hyphenated-string"

    def test_mixed_case_with_numbers(self):
        """Test mixed case strings with numbers."""
        assert slugify("Version 2.1.0 BETA") == "version-2-1-0-beta"

    def test_consecutive_special_chars(self):
        """Test consecutive special characters are collapsed."""
        assert (
            slugify("test...multiple!!!special???chars")
            == "test-multiple-special-chars"
        )


class TestGenerateUri:
    """Test cases for the generate_uri function."""

    def test_returns_string(self):
        """Test that generate_uri returns a string."""
        result = generate_uri()
        assert isinstance(result, str)

    def test_valid_uuid_format(self):
        """Test that the returned string is a valid UUID format."""
        result = generate_uri()
        # Should match UUID4 format: 8-4-4-4-12 hex digits
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        assert uuid_pattern.match(result) is not None

    def test_parseable_as_uuid(self):
        """Test that the returned string can be parsed as a UUID."""
        result = generate_uri()
        # Should not raise an exception
        parsed_uuid = uuid.UUID(result)
        assert str(parsed_uuid) == result

    def test_uniqueness(self):
        """Test that multiple calls generate different UUIDs."""
        results = [generate_uri() for _ in range(100)]
        # All results should be unique
        assert len(set(results)) == 100

    def test_version_4_uuid(self):
        """Test that generated UUIDs are version 4."""
        result = generate_uri()
        parsed_uuid = uuid.UUID(result)
        assert parsed_uuid.version == 4
