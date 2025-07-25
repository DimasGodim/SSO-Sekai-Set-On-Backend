from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    nickname: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    identification: str
    password: str

class VerificationMail(BaseModel):
    email: EmailStr
    verification_code: str

class UpdateProfile(BaseModel):
    nickname: Optional[str] = None
    name: Optional[str] = None