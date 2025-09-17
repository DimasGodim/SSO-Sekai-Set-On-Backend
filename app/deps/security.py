from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

import re

from fastapi import HTTPException

from configs import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    value = pwd_context.hash(password)
    return value

def verify_password(plain_password: str, hashed_password: str) -> bool:
    value = pwd_context.verify(plain_password, hashed_password)
    if not value:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    else:
        pass
    
def validate_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")


def create_access_token(email):
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.access_token_expire_minutes)
    data = {
        "sub": email,
        "exp": expire
    }
    return jwt.encode(data, config.secret_key, algorithm=config.algorithm)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
    except JWTError as e:    
        if str(e) == "JWT decode error: Signature has expired.":
            raise HTTPException(status_code=401, detail="Token is expired")
        else:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
def verification_access_token(access_token):
    if not access_token or not access_token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    
    token = access_token.split(" ")[1]
    payload = decode_access_token(token)

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    return email