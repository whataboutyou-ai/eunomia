from functools import lru_cache

from dotenv import load_dotenv
from pydantic import model_validator
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
    ENGINE_SQL_DATABASE_URL: str = "sqlite:///./.db/engine_db.sqlite"

    # Fetcher config
    FETCHERS: dict[str, dict] = {
        "internal": {"sql_database_url": "sqlite:///./.db/internal_db.sqlite"}
    }

    # Server config
    BULK_CHECK_MAX_REQUESTS: int = 100
    BULK_CHECK_BATCH_SIZE: int = 10

    # Admin API config
    ADMIN_API_ENABLED: bool = False
    ADMIN_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

    @model_validator(mode="after")
    def validate_admin_api_config(self) -> "Settings":
        """Validate that ADMIN_API_KEY is properly configured when ADMIN_API_ENABLED is True."""
        if self.ADMIN_API_ENABLED:
            if not self.ADMIN_API_KEY:
                raise ValueError(
                    "ADMIN_API_KEY must be set when ADMIN_API_ENABLED is True"
                )

            if len(self.ADMIN_API_KEY) < 12:
                raise ValueError(
                    "ADMIN_API_KEY must be at least 12 characters long for security"
                )

        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
