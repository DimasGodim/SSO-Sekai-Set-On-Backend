from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from data.act.base import (
    news_list,
    news_search,
    verification_api_key
)

from app.schema.response.success import success as success_response

router = APIRouter()

@router.get("/list")
async def list_news(api_key: str = Header(...)):
    await verification_api_key(key=api_key)
    result = await news_list()
    return JSONResponse(content=success_response(data=result), status_code=200)

@router.get("/search")
async def search_news(title: str, api_key: str = Header(...)):
    await verification_api_key(key=api_key)
    result = await news_search(titile=title)
    return JSONResponse(content=success_response(data=result), status_code=200)