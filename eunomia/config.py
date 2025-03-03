from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(override=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Eunomia Server"
    DEBUG: bool = False

    OPA_SERVER_HOST: str = "127.0.0.1"
    OPA_SERVER_PORT: int = 8181
    OPA_POLICY_PATH: str

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
