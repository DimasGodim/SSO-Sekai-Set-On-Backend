from fastapi import HTTPException

from data.db.mongo.models import User

from app.schema.post.auth import signup as schema_signup, verification as schema_verification

from app.deps.security import hash_password

async def signup(data: schema_signup, verification_code: str, db):
    existing_user = await db["users"].find_one({"email": data.email})

    if existing_user:
        if existing_user.get("activate", False):
            raise HTTPException(status_code=400, detail="Email already registered")
        else:  
            await db["users"].update_one(
                {"email": data.email},
                {"$set": {"verification_code": verification_code}}
            )
            return {
                "email": existing_user["email"],
                "name": existing_user["name"],
                "nickname": existing_user["nickname"]
            }

    if await db["users"].find_one({"nickname": data.nickname}):
        raise HTTPException(status_code=400, detail="Nickname already in use")

    obj = User(
        email=data.email,
        name=data.name,
        nickname=data.nickname,
        hashed_password=hash_password(data.password),
        activate=False,
        verification_code=verification_code,
    )

    await db["users"].insert_one(obj.model_dump())

    return {
        "email": obj.email,
        "name": obj.name,
        "nickname": obj.nickname
    }

async def verification(data: schema_verification, db):
    obj = await db["users"].find_one({"email": data.email})
    if not obj:
        raise HTTPException(status_code=400, detail="Email not registered")

    if obj["verification_code"] != data.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    await db["users"].update_one(
        {"email": data.email},
        {"$set": {"activate": True, "verification_code": None}}
    )

    return {
        "email": obj["email"],
        "name": obj["name"],
        "nickname": obj["nickname"]
    }


async def cek_user(identification, db):
    obj = await db["users"].find_one({
        "$or": [
            {"email": identification},
            {"nickname": identification}
        ]
    })

    if not obj:
        raise HTTPException(status_code=400, detail="User not found")

    if not obj.get("activate", False):
        raise HTTPException(
            status_code=403,
            detail="Account not activated. Please verify your email."
        )

    return {
        "email": obj["email"],
        "name": obj["name"],
        "nickname": obj["nickname"],
        "hashed_password": obj["hashed_password"]
    }