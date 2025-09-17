from pydantic import BaseModel, field_validator
from typing import Optional
from fastapi import HTTPException
from datetime import datetime

class ApikeyCreate(BaseModel):
    title: str
    detail: Optional[str] = None
    expired: Optional[int] = None

    @field_validator("expired")
    def validate_expired(cls, v):
        allowed = [7, 30, 60, 120, 365, None]
        if v not in allowed:
            raise HTTPException(detail="Invalid expiration value", status_code=400)
        return v

class ApiKeySaveLog(BaseModel):
    key: str
    endpoint: str
    method: str
    status_code: int
    timestamp: Optional[datetime] = None
    response_time: float