from fastapi import HTTPException
from datetime import datetime
from data.db.mongo.models import News

async def save(db, data):
    result = await db["news"].insert_one(data)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to save news")
    return {"status": "success"}

async def list(db):
    cursor = db["news"].find().sort("publish_at", -1).limit(20)
    news_list = await cursor.to_list(length=20)
    if not news_list:  
        return []
    return [
        {
            "title": n["title"],
            "summary": n["summary"],
            "content": n["content"],
            "link": n["link"],
            "published_at": (
                n["published_at"].isoformat()
                if isinstance(n["published_at"], datetime)
                else str(n["published_at"])
            ),
        }
        for n in news_list
    ]

async def search(db, title: str):
    cursor = (
        db["news"]
        .find({"title": {"$regex": title, "$options": "i"}})
        .sort("publish_at", -1)
        .limit(5)
    )
    news_list = await cursor.to_list(length=5)

    return{
            "news":[
                {
                    "title": n["title"],
                    "summary": n["summary"],
                    "content": n["content"],
                    "link": n["link"],
                    "published_at": (
                        n["published_at"].isoformat()
                        if isinstance(n["published_at"], datetime)
                        else str(n["published_at"])
                    ),
                }
                for n in news_list
            ],
        }
