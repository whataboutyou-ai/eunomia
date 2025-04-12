from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class Settings(BaseSettings):
    """
    Configuration settings for the Eunomia Server.

    This class uses Pydantic's BaseSettings to load and validate
    configuration from environment variables and the `.env` file.

    Attributes
    ----------
    PROJECT_NAME : str
        Name of the project. Defaults to "Eunomia Server".
    DEBUG : bool
        Flag to enable debug mode. Defaults to False.
    INTERNAL_SQL_DATABASE_URL : str
        Database connection string. Defaults to "sqlite:///.db/internal_db.sqlite".
    OPA_SERVER_HOST : str
        Host address for the Open Policy Agent server. Defaults to "127.0.0.1".
    OPA_SERVER_PORT : int
        Port for the Open Policy Agent server. Defaults to 8181.
    OPA_POLICY_FOLDER : str
        Path to the folder where the Rego policy files are stored. Required.
    """

    PROJECT_NAME: str = "Eunomia Server"
    DEBUG: bool = False

    INTERNAL_SQL_DATABASE_URL: str = "sqlite:///.db/internal_db.sqlite"

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
