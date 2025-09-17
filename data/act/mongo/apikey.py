from fastapi import HTTPException

from statistics import mean

import secrets

from datetime import datetime, timezone, timedelta

from data.db.mongo.models import APIKey, APIUsageLog

from app.schema.post.apikey import ApikeyCreate as schema_ApikeyCreate


async def information(email, db):
    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    api_keys = user.get("api_keys", [])

    if not api_keys:
        return {"api_keys":[]}

    response = []
    for key in api_keys:
        logs = await db["usage_logs"].find({"key": key["key"]}).to_list(length=None)

        total = len(logs)
        success_count = sum(1 for log in logs if 200 <= log.get("status_code", 0) <= 299)
        error_count = total - success_count
        avg_response = mean([log.get("response_time", 0) for log in logs]) if logs else 0.0

        response.append({
            "title": key.get("title"),
            "detail": key.get("detail"),
            "created_at": str(key.get("created_at")),
            "expired": str(key.get("expired")) if key.get("expired") else None,
            "usage_logs": [
                {
                    "endpoint": log.get("endpoint"),
                    "method": log.get("method"),
                    "status_code": log.get("status_code"),
                    "response_time": log.get("response_time"),
                    "timestamp": str(log.get("timestamp")),
                } for log in logs
            ],
            "usage_stats": {
                "total_usage": total,
                "success_count": success_count,
                "error_count": error_count,
                "avg_response_time": round(avg_response, 2),
            }
        })

    return {"api_keys": response}


async def create(email, data: schema_ApikeyCreate, db):
    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_title = await db["users"].find_one(
        {"email": email, "api_keys.title": data.title}
    )
    if existing_title:
        raise HTTPException(
            status_code=400,
            detail=f"An API key with the title '{data.title}' already exists for this email."
        )

    while True:
        token = secrets.token_urlsafe(32)
        existing = await db["users"].find_one({"api_keys.key": token})
        if not existing:
            break

    expired_at = None
    if data.expired is not None:
        expired_at = datetime.now(timezone.utc) + timedelta(days=int(data.expired))

    obj = APIKey(
        key=token,
        title=data.title,
        detail=data.detail,
        email=email,
        created_at=datetime.now(timezone.utc),
        expired=expired_at,
    )

    result = await db["users"].update_one(
        {"email": email},
        {"$push": {"api_keys": obj.model_dump()}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to create API Key")

    return {
        "title": str(obj.title),
        "detail": str(obj.detail),
        "key": f"ApiKey {str(obj.key)}",
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "expired": obj.expired.isoformat() if obj.expired else None,
    }


async def delete(title, email, db):
    result = await db["users"].update_one(
        {"email": email},
        {"$pull": {"api_keys": {"title": title}}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="API key not found")

from datetime import datetime, timezone

async def verification(db, key):
    if key and key.startswith("ApiKey "):
        value = key.split(" ")[1]
    elif not key:
        raise HTTPException(status_code=401, detail="API key required")
    
    user = await db["users"].find_one(
        {"api_keys.key": value},
        {"api_keys.$": 1} 
    )

    if not user or "api_keys" not in user or len(user["api_keys"]) == 0:
        raise HTTPException(status_code=403, detail="Invalid API key")

    api_key = user["api_keys"][0]  

    if api_key.get("expired"):
        expired_at = api_key["expired"]

        if expired_at.tzinfo is None:
            expired_at = expired_at.replace(tzinfo=timezone.utc)

        if expired_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=403, detail="API key expired")
    
    return api_key["email"]


async def save_log(db, data: dict):
    try:
        result = await db["usage_logs"].insert_one(data)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to save log")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving log: {str(e)}")
