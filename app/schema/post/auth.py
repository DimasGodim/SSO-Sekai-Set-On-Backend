from pydantic import BaseModel, EmailStr
from typing import Optional

class signup(BaseModel):
    name: str
    nickname: str
    email: EmailStr
    password: str

class signin(BaseModel):
    identification: str
    password: str

class verification(BaseModel):
    email: EmailStr
    verification_code: str