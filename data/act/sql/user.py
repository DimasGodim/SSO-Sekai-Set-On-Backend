from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schema.post.user import UpdateProfile as schema_UpdateProfile
from data.db.sql.models import User

async def get(email, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    obj = result.scalars().first()
    
    if not obj:
        raise HTTPException(status_code=400, detail="Account Not Found")
    
    return {
        "name": str(obj.name),
        "nickname": str(obj.nickname),
        "email": str(obj.email),
    }

async def update(db: AsyncSession, email: str, data: schema_UpdateProfile):
    result = await db.execute(select(User).where(User.email == email))
    obj = result.scalars().first()

    if not obj:
        raise HTTPException(status_code=404, detail="Account Not Found")

    if data.name is not None:
        obj.name = data.name.strip()
    if data.nickname is not None:
        obj.nickname = data.nickname.strip()

    await db.commit()
    await db.refresh(obj)

    return {
        "name": obj.name,
        "nickname": obj.nickname,
        "email": obj.email,
    }

async def delete(db: AsyncSession, email):
    result = await db.execute(select(User).where(User.email == email))
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(status_code=400, detail="Account Not Found")
    
    await db.delete(obj)
    await db.commit()