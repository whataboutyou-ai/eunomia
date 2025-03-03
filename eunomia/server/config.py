import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Eunomia Server"
    DEBUG: bool = False
    FRONTEND_URL: str = "*"
    OPA_SERVER_URL: str = "127.0.0.1"
    OPA_SERVER_PORT: int = 8181
    OPA_POLICY_PATH: str = ""

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:

    return Settings()


settings = get_settings()
