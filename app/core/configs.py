from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    database_url: str
    email: str
    password_email: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    origins: List[str] = []
    
    class Config:
        env_file = ".env"

config = Settings()
