from functools import lru_cache

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
    ENGINE_SQL_DATABASE_URL: str = "sqlite:///.db/engine_db.sqlite"

    # Fetcher config
    FETCHERS: dict[str, dict] = {
        "internal": {"SQL_DATABASE_URL": "sqlite:///.db/internal_db.sqlite"}
    }

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
