from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from data.db.sql.models import RefreshToken

from configs import config

from datetime import datetime, timezone, timedelta

async def save_refresh_token(token, email, db: AsyncSession):
    db.add(RefreshToken(
        token=token, 
        email=email, 
        created_at=datetime.now(timezone.utc),
        expired=datetime.now(timezone.utc) + timedelta(days=config.refersh_token_exp_day)
        ))
    
    await db.commit()

async def cek_refresh_token(token: str, email: str, db: AsyncSession):
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.email == email
        )
    )
    refresh_token = result.scalar_one_or_none()

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token or email")

    if refresh_token.expired < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

async def delete_refresh_token(token: str, email: str, db: AsyncSession):
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.email == email
        )
    )
    refresh_token = result.scalar_one_or_none()

    if not refresh_token:
        raise HTTPException(status_code=404, detail="Refresh token not found")

    await db.delete(refresh_token)
    await db.commit()