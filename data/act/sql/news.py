from fastapi import HTTPException

from data.db.sql.models import News

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

async def save(db: AsyncSession, data):
    obj = News(
        title=data["title"],
        link=data["link"],
        published_at=data["published_at"],
        summary=data["summary"],
        content=data["content"],
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

async def list(db: AsyncSession):
    result = await db.execute(
        select(News).order_by(News.published_at.desc()).limit(20)
    )
    news_list = result.scalars().all()
    if not news_list:
        return []
    return [
        {
            "title": str(n.title),
            "summary": str(n.summary),
            "content": str(n.content),
            "link": str(n.link),
            "published_at": n.published_at.isoformat()
        } for n in news_list
    ]

async def search(db: AsyncSession, title):
    query = (
        select(News)
        .where(News.title.ilike(f"%{title}%"))
        .order_by(News.published_at.desc())
        .limit(5)
    )

    result = await db.execute(query)
    news = result.scalars().all()

    return{
            "news":[
                {
                    "title": n.title,
                    "summary": n.summary,
                    "content": n.content,
                    "link": n.link,
                    "published_at": n.published_at.isoformat()
                }
                for n in news
            ]
        }
