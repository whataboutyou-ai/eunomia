import uuid


def generate_uri() -> str:
    return str(uuid.uuid4())
