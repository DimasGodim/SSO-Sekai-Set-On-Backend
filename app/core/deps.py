from fastapi import Request, HTTPException, Depends, Header
from app.db.database import get_db
from app.db.models import APIKey, user
from app.core.security import decode_access_token
from sqlalchemy.orm import Session
from datetime import datetime

def verify_api_key(request: Request, db: Session = Depends(get_db)) -> APIKey:
    key = None

    # 1. Coba ambil dari Authorization header dengan prefix ApiKey
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("ApiKey "):
        key = auth_header.split(" ")[1]

    # 2. Atau fallback ke header x-api-key
    if not key:
        key = request.headers.get("x-api-key")

    if not key:
        raise HTTPException(status_code=401, detail="API key required")

    key_obj = db.query(APIKey).filter(APIKey.key == key).first()

    if not key_obj:
        raise HTTPException(status_code=403, detail="Invalid API key")

    if key_obj.expired and key_obj.expired < datetime.utcnow():
        raise HTTPException(status_code=403, detail="API key expired")

    return key_obj

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")

    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user_obj = db.query(user).filter(user.id == int(user_id)).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    return user_obj
