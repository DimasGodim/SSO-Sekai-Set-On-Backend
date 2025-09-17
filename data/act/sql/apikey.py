from fastapi import HTTPException

from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, and_

from app.schema.post.apikey import ApikeyCreate as schema_ApikeyCreate

import secrets

from datetime import datetime, timezone, timedelta

from data.db.sql.models import APIKey, APIUsageLog

async def information(email, db: AsyncSession):
    result = await db.execute(
        select(APIKey)
        .options(selectinload(APIKey.usage_logs))
        .where(APIKey.email == email)
    )
    api_keys = result.scalars().all()

    if not api_keys:
        return {"api_keys":[]}
    
    api_key_values = [key.key for key in api_keys]

    usage_stats = {}
    if api_key_values:
        stat_result = await db.execute(
            select(
                APIUsageLog.key.label("api_key"),
                func.count().label("total_usage"),
                func.sum(
                    case((APIUsageLog.status_code.between(200, 299), 1), else_=0)
                ).label("success_count"),
                func.sum(
                    case((~APIUsageLog.status_code.between(200, 299), 1), else_=0)
                ).label("error_count"),
                func.avg(APIUsageLog.response_time).label("avg_response_time"),
            )
            .where(APIUsageLog.key.in_(api_key_values))
            .group_by(APIUsageLog.key)
        )
        usage_stats = {row.api_key: row for row in stat_result}

    return {
        "api_keys": [
            {
                "title": key.title,
                "detail": key.detail,
                "created_at": str(key.created_at),
                "expired": str(key.expired) if key.expired else None,
                "usage_logs": [
                    {
                        "endpoint": log.endpoint,
                        "method": log.method,
                        "status_code": log.status_code,
                        "response_time": log.response_time,
                        "timestamp": str(log.timestamp),
                    }
                    for log in key.usage_logs
                ],
                "usage_stats": {
                    "total_usage": (stats.total_usage if (stats := usage_stats.get(key.key)) else 0),
                    "success_count": (stats.success_count if stats else 0),
                    "error_count": (stats.error_count if stats else 0),
                    "avg_response_time": (
                        round(stats.avg_response_time, 2) if stats and stats.avg_response_time else 0.0
                    ),
                }
            }
            for key in api_keys
        ]
    }

async def create(email: str, data: schema_ApikeyCreate, db: AsyncSession):
    result = await db.execute(
        select(APIKey).where(APIKey.email == email, APIKey.title == data.title)
    )
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"An API key with the title '{data.title}' already exists for this email."
        )

    expired_at = None
    if data.expired is not None:
        expired_at = datetime.now(timezone.utc) + timedelta(days=int(data.expired))

    while True:
        key_value = secrets.token_urlsafe(32)

        obj = APIKey(
            email=email,
            key=key_value,
            title=data.title,
            detail=data.detail,
            created_at=datetime.now(timezone.utc),
            expired=expired_at
        )

        db.add(obj)
        try:
            await db.commit()
            await db.refresh(obj)
            return {
                "title": str(obj.title),
                "detail": str(obj.detail),
                "key": f"ApiKey {str(obj.key)}",
                "created_at": obj.created_at.isoformat() if obj.created_at else None,
                "expired": obj.expired.isoformat() if obj.expired else None,
            }

        except IntegrityError:
            await db.rollback()


async def delete(title, email, db: AsyncSession):
    result = await db.execute(select(APIKey).where(and_(APIKey.title == title, APIKey.email == email)))
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(status_code=404, detail="API key not found")
    
    await db.delete(obj)
    await db.commit()

async def verification(db: AsyncSession, key):
    if key and key.startswith("ApiKey "):
        value = key.split(" ")[1]
    elif not key:
        raise HTTPException(status_code=401, detail="API key required")
    
    result = await db.execute(select(APIKey).where(APIKey.key == value))
    obj = result.scalars().first()

    if not obj:
        raise HTTPException(status_code=403, detail="Invalid API key")

    if obj.expired and obj.expired < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="API key expired")
    
    return obj.email
    
async def save_log(db: AsyncSession, data: dict ):
    data: APIUsageLog = APIUsageLog(**data)
    db.add(data)
    await db.commit()
    await db.refresh(data)
