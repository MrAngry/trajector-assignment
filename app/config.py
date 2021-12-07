from typing import List

from pydantic import BaseSettings, AnyHttpUrl



class Settings(BaseSettings):

    PROJECT_NAME: str
    DB_URL: str
    DOMAIN:str
    TEST_DB_URL: str
    API_V1_STR: str = "/api/v1"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    UPLOADS_FOLDER = "/app/static/user_uploads"
    STATIC_URL = '/static'

settings = Settings()

TORTOISE_ORM = {
    "connections": {"default": settings.DB_URL},
    "apps"       : {
        "models": {
            "models"            : ["models.item","models.tag"],
            "default_connection": "default",
        },
    },
}