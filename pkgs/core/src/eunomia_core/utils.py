import re
import unicodedata
import uuid


def generate_uri() -> str:
    return str(uuid.uuid4())


def slugify(s: str) -> str:
    s = s.lower()

    # Normalize Unicode characters (e.g., emojis, accented characters)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("utf-8")

    # Replace any character that is not an alphanumeric or hyphen with a hyphen
    s = re.sub(r"[^\w-]", "-", s)

    # Replace multiple consecutive hyphens with a single hyphen
    s = re.sub(r"-+", "-", s)

    return s.strip("-")
