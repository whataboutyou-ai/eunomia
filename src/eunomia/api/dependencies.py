from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from eunomia.config import settings

api_key_header = APIKeyHeader(name="WAY-API-KEY", auto_error=False)


async def validate_api_key(api_key: str = Security(api_key_header)) -> None:
    """Validate the API key"""
    if settings.ADMIN_API_KEY is not None and api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key. Please provide a valid API key.",
        )
