from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RefershToken(BaseModel):
    token: str
    email: str
    created_at: datetime

class News(BaseModel):
    title = str
    link = str
    publish_at = datetime
    summary = str
    content = str
    source: str

class APIUsageLog(BaseModel):
    endpoint: str
    response_time: float
    method: str
    timestamp: datetime
    status_code: int

class APIKey(BaseModel):
    title: str
    detail: str
    key: str
    email: str
    created_at: datetime
    expired: datetime
    sequence: int
    log: APIUsageLog

class user(BaseModel):
    email: str
    name: str
    nickname: str
    hashed_password: str
    activate: bool
    verification_code: str
    api_key: APIKey
    refersh_token: RefershToken
