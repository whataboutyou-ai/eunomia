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

    # Fetcher config
    FETCHERS: dict[str, dict] = {
        "internal": {"SQL_DATABASE_URL": "sqlite:///.db/internal_db.sqlite"}
    }

    # Engine configs
    OPA_SERVER_HOST: str = "127.0.0.1"
    OPA_SERVER_PORT: int = 8181
    OPA_POLICY_FOLDER: str

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
