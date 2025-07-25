from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.deps import get_current_user
from app.db.models import APIKey, user, APIUsageLog
from app.service.mail import send_api_key_created_email
from datetime import datetime
import secrets

router = APIRouter()

@router.post("/create")
def create_api_key(
    title: str = None,
    db: Session = Depends(get_db),
    current_user: user = Depends(get_current_user)
):
    created_time = datetime.now()
    key = secrets.token_urlsafe(32)
    count = db.query(APIKey).filter(APIKey.user_id == current_user.id).count()
    sequence_number = count + 1

    new_key = APIKey(
        key=key,
        user_id=current_user.id,
        sequence=sequence_number,
        title=title
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    send_api_key_created_email(
        email=current_user.email,
        title=title,
        created_at=created_time
    )

    return JSONResponse(
        status_code=201,
        content={
            "status": "success",
            "message": "API key created. Please save it. It will not be shown again.",
            "api_key": key,
            "identifier": f"{current_user.id}-{sequence_number}"
        }
    )

@router.get("/list")
def list_api_keys(current_user: user = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "total": len(keys),
            "keys": [
                {
                    "identifier": f"{key.user_id}-{key.sequence}",
                    "created_at": key.created_at.isoformat(),
                    "title": key.title,
                    "usage_count": len(key.usage_logs)
                }
                for key in keys
            ]
        }
    )

@router.delete("/delete/{identifier}")
def delete_api_key(identifier: str, db: Session = Depends(get_db), current_user: user = Depends(get_current_user)):
    try:
        user_id_str, seq_str = identifier.split("-")
        user_id = int(user_id_str)
        sequence = int(seq_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid identifier format")

    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your API key")

    api_key = db.query(APIKey).filter_by(user_id=user_id, sequence=sequence).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(api_key)
    db.commit()

    return JSONResponse(status_code=200, content={"status": "success", "message": "API key deleted"})

@router.get("/usage")
def get_usage_by_key(
    current_user: user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()

    usage_summary = []
    total_requests_all_keys = 0

    for key in keys:
        logs = [
            {
                "endpoint": log.endpoint,
                "method": log.method,
                "status_code": log.status_code,
                "timestamp": log.timestamp.isoformat()
            }
            for log in key.usage_logs  # pastikan relasi `usage_logs` di model APIKey
        ]

        usage_summary.append({
            "identifier": f"{key.user_id}-{key.sequence}",
            "title": key.title,  # jika kamu simpan nama/titlenya
            "total_requests": len(logs),
            "logs": logs
        })

        total_requests_all_keys += len(logs)

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "total_requests": total_requests_all_keys,
            "data": usage_summary
        }
    )
