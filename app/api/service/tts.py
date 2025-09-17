from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from data.act.base import (
    char as char_act,
    verification_api_key as verification_api_key_act,
)

from app.service.voicevox import request_audio

from app.schema.response.success import success as success_response

router = APIRouter()

@router.post("/change")
async def char(text: str, speaker: int, api_key: str = Header(...)):
    await verification_api_key_act(key=api_key)
    audio = request_audio(text=text, speaker_id=speaker)
    return JSONResponse(content=success_response(data=audio), status_code=200)

@router.get("/char")
async def get_char(api_key: str = Header(...)):
    await verification_api_key_act(key=api_key)
    result = char_act()
    return JSONResponse(content=success_response(data=result), status_code=200)