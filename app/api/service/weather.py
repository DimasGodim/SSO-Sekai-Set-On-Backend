from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from app.service.weather import get_weather
from app.schema.response.success import success as success_response

router = APIRouter()

@router.get("/current")
async def current_weather(city: str, api_key: str = Header(...)):
    result = get_weather(city)
    return JSONResponse(content=success_response(data=result), status_code=200)