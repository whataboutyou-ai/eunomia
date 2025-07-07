from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class Settings(BaseSettings):
    """
    Configuration settings for the Eunomia Server.

    This class uses Pydantic's BaseSettings to load and validate
    configuration from environment variables and the `.env` file.
    """

    PROJECT_NAME: str = "Eunomia Server"
    DEBUG: bool = False

    # Engine config
    ENGINE_SQL_DATABASE_URL: str = "sqlite:///./.db/eunomia_db.sqlite"

    # Fetcher config
    FETCHERS: dict[str, dict] = {
        "registry": {"sql_database_url": "sqlite:///./.db/eunomia_db.sqlite"}
    }

    # Server config
    ADMIN_API_KEY: Optional[str] = None
    BULK_CHECK_MAX_REQUESTS: int = 100
    BULK_CHECK_BATCH_SIZE: int = 10

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
