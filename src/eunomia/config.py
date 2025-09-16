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
    ENGINE_SQL_DATABASE: bool = True
    ENGINE_SQL_DATABASE_URL: str = "sqlite:///./.db/eunomia_db.sqlite"

    # Fetcher config
    FETCHERS: dict[str, dict] = {
        "registry": {"sql_database_url": "sqlite:///./.db/eunomia_db.sqlite"}
    }

    # OPA config
    OPA_BASE_URL: str = "http://localhost:8181"
    OPA_POLICY_PATH: str = "eunomia/allow"
    OPA_TIMEOUT: int = 30

    # Server config
    ADMIN_AUTHN_REQUIRED: bool = False
    ADMIN_API_KEY: str = ""
    BULK_CHECK_MAX_REQUESTS: int = 100
    BULK_CHECK_BATCH_SIZE: int = 10

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

    @model_validator(mode="after")
    def validate_api_key_when_required(self) -> "Settings":
        if self.ADMIN_AUTHN_REQUIRED and not self.ADMIN_API_KEY:
            raise ValueError(
                "ADMIN_API_KEY is required when ADMIN_AUTHN_REQUIRED is true"
            )
        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
