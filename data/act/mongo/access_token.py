from fastapi import HTTPException

from datetime import datetime, timezone, timedelta

from data.db.mongo.models import RefreshToken

from configs import config

async def save_refresh_token(token: str, email: str, db):
    obj = RefreshToken(
        token=token,
        created_at=datetime.now(timezone.utc),
        expired=datetime.now(timezone.utc) + timedelta(days=config.refersh_token_exp_day)
    )

    result = await db["users"].update_one(
        {"email": email},
        {"$push": {"refresh_tokens": obj.model_dump()}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")


async def cek_refresh_token(token: str, email: str, db):
    obj = await db["users"].find_one(
        {"email": email, "refresh_tokens.token": token},
        {"refresh_tokens.$": 1, "email": 1}
    )

    if not obj or "refresh_tokens" not in obj or not obj["refresh_tokens"]:
        raise HTTPException(status_code=401, detail="Invalid refresh token or email")

    refresh_token = obj["refresh_tokens"][0]

    if refresh_token["expired"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

async def delete_refresh_token(token: str, email: str, db):
    result = await db["users"].update_one(
        {"email": email},
        {"$pull": {"refresh_tokens": {"token": token}}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Refresh token not found")