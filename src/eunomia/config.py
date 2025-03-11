from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

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
    LOCAL_DB_HOST : str
        Database connection string. Defaults to "sqlite:///db.sqlite".
    OPA_SERVER_HOST : str
        Host address for the Open Policy Agent server. Defaults to "127.0.0.1".
    OPA_SERVER_PORT : int
        Port for the Open Policy Agent server. Defaults to 8181.
    OPA_POLICY_PATH : str
        Path to the OPA policy file. Required.
    """

    PROJECT_NAME: str = "Eunomia Server"
    DEBUG: bool = False

    LOCAL_DB_HOST: str = "sqlite:///db.sqlite"

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
