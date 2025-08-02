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
    origins: str = ""
    origins_public: str
    
    class Config:
        env_file = ".env"
    
    @property
    def origins_list(self) -> List[str]:
        """Convert CSV string to list"""
        if self.origins:
            return [origin.strip() for origin in self.origins.split(",")]
        return []

config = Settings()
