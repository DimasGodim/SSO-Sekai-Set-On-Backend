from fastapi import HTTPException

from data.db.mongo.models import User

from app.schema.post.user import UpdateProfile as schema_UpdateProfile

async def get(email, db):
    obj = await db["users"].find_one({"email": email})
    if not obj:
        raise HTTPException(status_code=400, detail="Account Not Found")
    
    return{
        "name": obj.get("name"),
        "nickname": obj.get("nickname"),
        "email": obj.get("email"),
    }
    
async def update(db, email: str, data: schema_UpdateProfile):
    obj = await db["users"].find_one({"email": email})
    if not obj:
        raise HTTPException(status_code=404, detail="Account Not Found")

    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.nickname is not None:
        update_data["nickname"] = data.nickname

    if update_data:
        result = await db["users"].update_one(
            {"email": email},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=400, detail="Account Not Found")

        obj = await db["users"].find_one({"email": email})

    return {
        "name": obj.get("name"),
        "nickname": obj.get("nickname"),
        "email": obj.get("email"),
    }

async def delete(db, email):
    result = await db["users"].delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=400, detail="Account Not Found")

