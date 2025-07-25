from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str
    email: str
    password_email: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    class Config:
        env_file = ".env"

config = Settings()
