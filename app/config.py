from typing import List

from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    PROJECT_NAME: str
    DB_URL: str
    DOMAIN: str
    TEST_DB_URL: str
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    UPLOADS_FOLDER = "/app/static/user_uploads"
    STATIC_URL = '/static'
    DOWNLOAD_RETRIES = 1
    DOWNLOAD_TIMEOUT = 5  # In seconds


settings = Settings()

TORTOISE_ORM = {
    "connections": {"default": settings.DB_URL},
    "apps"       : {
        "models": {
            "models"            : ["models.item", "models.tag"],
            "default_connection": "default",
        },
    },
}