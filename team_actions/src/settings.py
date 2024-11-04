import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    team_id: str = "c44cd9dd-4929-4fb1-82c0-f93a26c8e937"
    backend_api: str = "https://aes-agniachallenge-case.olymp.innopolis.university/"
    root_directory: str = os.path.dirname(__file__)


settings = Settings()
