import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Common
    app_env: str

    # Key
    secret_key: str

    # OAuth
    google_client_id: str
    google_client_secret: str
    naver_client_id: str
    naver_client_secret: str
    kakao_client_id: str
    kakao_client_secret: str

    # URLs
    domain: str = ".escape-note.com"
    front_main_url: str = "https://escape-note.com"
    front_signup_url: str = "https://escape-note.com/accounts/signup/social"
    backend_url: str = "https://api.escape-note.com"

    def __init__(self):
        super().__init__()

        if os.getenv("APP_ENV") == "local":
            self.domain = "localhost"
            self.front_main_url = "http://localhost:3000"
            self.front_signup_url = "http://localhost:3000/accounts/signup/social"
            self.backend_url = "http://localhost:8000"


settings = Settings()
