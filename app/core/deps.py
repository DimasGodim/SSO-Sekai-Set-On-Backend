from fastapi import Request, HTTPException, Depends, Header
from app.db.database import get_db
from app.db.models import APIKey, user
from app.core.security import decode_access_token
from sqlalchemy.orm import Session
from datetime import datetime

def verify_api_key(request: Request, db: Session = Depends(get_db)) -> APIKey:
    key = request.headers.get("api_key")
    if not key:
        raise HTTPException(status_code=401, detail="API key required")

    key_obj = db.query(APIKey).filter(APIKey.key == key).first()
    if not key_obj:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    if key_obj.expired_at and key_obj.expired_at < datetime.utcnow():
        raise HTTPException(status_code=403, detail="API key expired")

    return key_obj

def verify_api_key(api_key: str = Header(...), db: Session = Depends(get_db)):
    api_key = db.query(APIKey).filter(APIKey.key == api_key).first()
    if not api_key:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key

def get_current_user(access_token: str = Header(...), db: Session = Depends(get_db)):
    payload = decode_access_token(access_token)
    user_id = payload.get("sub")
    if not payload:
        raise HTTPException(status_code=404, detail="Access token not found")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_obj = db.query(user).filter(user.id == int(user_id)).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    return user_obj
