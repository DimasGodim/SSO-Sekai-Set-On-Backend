from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.deps import get_current_user
from app.db.models import user as UserModel
from app.schema import UpdateProfile

router = APIRouter()

from collections import defaultdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.db.models import user, APIKey, APIUsageLog
from app.core.deps import get_current_user, get_db

router = APIRouter()

@router.get("/detail")
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: user = Depends(get_current_user)
):
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    api_key_ids = [key.id for key in api_keys]

    # Ambil semua log pemakaian
    usage_logs = (
        db.query(
            APIUsageLog.api_key_id,
            APIUsageLog.endpoint,
            APIUsageLog.method,
            APIUsageLog.timestamp,
            APIUsageLog.status_code,
            APIUsageLog.response_time
        )
        .filter(APIUsageLog.api_key_id.in_(api_key_ids))
        .all()
    )

    # Statistik penggunaan per API key
    usage_stats = db.query(
        APIUsageLog.api_key_id,
        func.count().label("total_usage"),
        func.sum(
            case((APIUsageLog.status_code.between(200, 299), 1), else_=0)
        ).label("success_count"),
        func.sum(
            case((~APIUsageLog.status_code.between(200, 299), 1), else_=0)
        ).label("error_count"),
        func.avg(APIUsageLog.response_time).label("avg_response_time") 
    ).filter(APIUsageLog.api_key_id.in_(api_key_ids)).group_by(APIUsageLog.api_key_id).all()


    # Kelompokkan log berdasarkan API key
    logs_by_key = defaultdict(list)
    for log in usage_logs:
        logs_by_key[log.api_key_id].append({
            "endpoint": log.endpoint,
            "method": log.method,
            "timestamp": str(log.timestamp),
            "status_code": log.status_code,
            "response_time": log.response_time or "0ms"
        })

    # Statistik per API key
    stats_by_key = {
        stat.api_key_id: {
            "total_usage": stat.total_usage,
            "success_rate": (stat.success_count / stat.total_usage * 100) if stat.total_usage else 0,
            "error_rate": (stat.error_count / stat.total_usage * 100) if stat.total_usage else 0,
            "avg_response_time": round(stat.avg_response_time, 2) if stat.avg_response_time else 0.0
        }
        for stat in usage_stats
    }

    # Build response
    api_keys_data = []
    total_usage_all = 0
    total_success_all = 0
    total_error_all = 0
    all_response_times = []

    for key in api_keys:
        stats = stats_by_key.get(key.id, {
            "total_usage": 0,
            "success_rate": 0,
            "error_rate": 0,
            "avg_response_time": 0
        })
        total_usage = stats["total_usage"]
        success_rate = stats["success_rate"]
        error_rate = stats["error_rate"]
        avg_response_time = stats["avg_response_time"]

        total_usage_all += total_usage
        total_success_all += total_usage * (success_rate / 100)
        total_error_all += total_usage * (error_rate / 100)
        all_response_times.append(avg_response_time)

        api_keys_data.append({
            "identifier": f"{key.user_id}-{key.sequence}",
            "title": key.title,
            "detail": key.detail,
            "created_at": str(key.created_at),
            "expired": str(key.expired),
            "total_usage": total_usage,
            "   ": round(success_rate, 2),
            "error_rate": round(error_rate, 2),
            "average_response_time": round(avg_response_time, 2),
            "usage_logs": logs_by_key.get(key.id, [])
        })

    average_success_rate = (total_success_all / total_usage_all * 100) if total_usage_all else 0
    average_error_rate = (total_error_all / total_usage_all * 100) if total_usage_all else 0
    average_response_time = round(sum(all_response_times) / len(all_response_times), 2) if all_response_times else 0

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": {
                "user_id": current_user.id,
                "name": current_user.name,
                "nickname": current_user.nickname,
                "email": current_user.email,
                "activate": current_user.activate,
                "total_api_keys": len(api_keys),
                "total_api_usage": total_usage_all,
                "average_success_rate": round(average_success_rate, 2),
                "average_error_rate": round(average_error_rate, 2),
                "average_response_time": average_response_time,
                "api_keys": api_keys_data
            }
        }
    )

@router.patch("/update")
def update_profile(
    profile: UpdateProfile,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    update_data = profile.dict(exclude_unset=True)

    # Validasi nickname jika ingin diubah
    if "nickname" in update_data:
        new_nickname = update_data["nickname"]
        if new_nickname != current_user.nickname:
            existing = db.query(UserModel).filter(
                UserModel.nickname == new_nickname,
                UserModel.id != current_user.id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Nickname already in use")
            current_user.nickname = new_nickname

    # Update name jika ada
    if "name" in update_data:
        current_user.name = update_data["name"]

    db.commit()
    db.refresh(current_user)

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Profile updated",
            "data": {
                "user_id": current_user.id,
                "name": current_user.name,
                "nickname": current_user.nickname,
                "email": current_user.email
            }
        }
    )

@router.delete("/delete")
def delete_account(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db.delete(current_user)
    db.commit()
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Account deleted"
        }
    )
