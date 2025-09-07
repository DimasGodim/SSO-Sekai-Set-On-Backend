from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from app.db.sql.client import get_db
from app.db.sql.models import News

from app.service.nhk import fetch_nhk_news

from app.core.deps import verify_api_key


router = APIRouter()

@router.get("/list")
def get_news(
    db: Session = Depends(get_db),
    api_key=Depends(verify_api_key)
):
    fetch_nhk_news(db)
    news_list = db.query(News).order_by(News.published_at.desc()).limit(20).all()
    return JSONResponse(
        content={
            "status": "success",
            "total": len(news_list),
            "data": [
                {
                    "title": n.title,
                    "summary": n.summary,
                    "content": n.content,
                    "link": n.link,
                    "published_at": n.published_at.isoformat()
                } for n in news_list
            ]
        }
    )

@router.get("/filter")
def get_news(
    title: str = Query(..., description="Filter by news title"),
    db: Session = Depends(get_db),
    api_key=Depends(verify_api_key)
):
    fetch_nhk_news(db)
    news = db.query(News).filter(News.title.ilike(f"%{title}%")).order_by(News.published_at.desc()).limit(5).all()
    return JSONResponse(
        content={
            "status": "success",
            "total": len(news),
            "data": [
                {
                    "title": n.title,
                    "summary": n.summary,
                    "content": n.content,
                    "link": n.link,
                    "published_at": n.published_at.isoformat()
                } for n in news
            ]
        }
    )