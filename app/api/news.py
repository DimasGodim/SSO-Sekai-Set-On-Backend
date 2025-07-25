from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import News

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