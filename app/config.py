from pydantic import BaseSettings


class Settings(BaseSettings):
    # Common
    app_env: str

    # Key
    at_secret: str
    rt_secret: str



settings = Settings()
