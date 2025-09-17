from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from data.db.sql.models import User

from app.schema.post.auth import signup as schema_signup, verification as schema_verification

from app.deps.security import hash_password

async def signup(data: schema_signup, verification_code: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalars().first()

    if existing_user:
        if existing_user.activate is True:  
            raise HTTPException(status_code=400, detail="Email already registered")
        else:  
            existing_user.verification_code = verification_code
            db.add(existing_user)
            await db.commit()
            await db.refresh(existing_user)
            return {
                "email": existing_user.email,
                "name": existing_user.name,
                "nickname": existing_user.nickname,
                "message": "Verification code updated"
            }

    result = await db.execute(select(User).where(User.nickname == data.nickname))
    filter_name = result.scalars().first()
    if filter_name:
        raise HTTPException(status_code=400, detail="Nickname already in use")

    obj = User(
        email=data.email,
        name=data.name,
        nickname=data.nickname,
        hashed_password=hash_password(data.password),
        verification_code=verification_code,
        activate=False
    )

    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    return {
        "email": obj.email,
        "name": obj.name,
        "nickname": obj.nickname,
    }


async def verification(data: schema_verification, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email))
    
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(status_code=400, detail="Email not registered")
    
    if obj.verification_code != data.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    obj.activate = True
    obj.verification_code = None
    
    await db.commit()

    return {
        "email": obj.email,
        "name": obj.name,
        "nickname": obj.nickname
    }

async def cek_user(identification, db: AsyncSession):
    result = await db.execute(
        select(User).where(
            or_(
                User.email == identification,
                User.nickname == identification,
            )
        )
    )
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(status_code=400, detail="User not found")

    if not obj.activate:
        raise HTTPException(status_code=403, detail="Account not activated. Please verify your email.") 

    return {
        "email": obj.email,
        "name": obj.name,
        "nickname": obj.nickname,
        "hashed_password": obj.hashed_password
    }