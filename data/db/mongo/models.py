from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RefreshToken(BaseModel):
    token: str
    created_at: datetime
    expired: datetime

class APIUsageLog(BaseModel):
    key: str
    endpoint: str
    response_time: float
    method: str
    timestamp: datetime
    status_code: int

class APIKey(BaseModel):
    title: str
    detail: Optional[str] = None
    key: str
    email: str
    created_at: datetime
    expired: Optional[datetime] = None

class News(BaseModel):
    title: str
    link: str
    published_at: datetime
    summary: str
    content: str

class User(BaseModel):
    email: str
    name: str
    nickname: str
    hashed_password: str
    activate: bool = False
    verification_code: Optional[str] = None
    api_keys: List[APIKey] = []
    refresh_tokens: List[RefreshToken] = []

    class Config:
        from_attributes  = True
        extra = "allow"
