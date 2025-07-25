from app.db.database import get_db
from app.core.deps import verify_api_key

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from pathlib import Path

import requests
import json

router = APIRouter()

def request_audio(text: str, speaker_id: int):
    try:
        url = 'https://api.tts.quest/v3/voicevox/synthesis/'
        params = {
            'speaker': speaker_id, 
            'text': text
        }
        response = requests.get(url, params=params)
        data = response.json()
        download = data.get('mp3DownloadUrl')
        streaming = data.get('mp3StreamingUrl') 
        return {
            'status': True,
            'download_audio': download,
            'streaming_audio': streaming
        }
    
    except Exception as e:
        return {
            'status': False,
            'penyebab': str(e)
        }

def normalize(text: str) -> str:
    return text.strip().lower()

@router.get('/list')
def list_voicevox_characters(
    db: Session = Depends(get_db),
    api_key=Depends(verify_api_key)
):
    try:
        file_path = Path("app/static/character.json")
        with open(file_path, "r", encoding="utf-8") as f:
            character_data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load character data: {e}")

    result = []
    for char in character_data:
        for style in char.get("styles", []):
            result.append({
                "character": char["name"],
                "style": style["name"],
                "speaker_id": style["id"]
            })

    return JSONResponse(content={'status': 'success', 'data': result})    

@router.get('/change')
def tts(
    char: str = Query(...),
    mode: str = Query(...), 
    text: str = Query(...), 
    db: Session = Depends(get_db),
    api_key=Depends(verify_api_key)
):
    try:
        with open("app/static/character.json", "r", encoding="utf-8") as f:
            characters = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load character.json: {str(e)}")

    # Cari karakter dan mode
    speaker_id = None
    for ch in characters:
        if normalize(ch["name"]) == normalize(char):
            for style in ch["styles"]:
                if normalize(style["name"]) == normalize(mode):
                    speaker_id = style["id"]
                    break
            break

    if speaker_id is None:
        raise HTTPException(status_code=404, detail="Character or mode not found")

    # Request audio
    result = request_audio(text=text, speaker_id=speaker_id)
    if not result["status"]:
        raise HTTPException(status_code=500, detail=f"TTS request failed: {result['penyebab']}")

    response = {
        "character": char,
        "mode": mode,
        "text": text,
        "download_url": result["download_audio"],
        "streaming_url": result["streaming_audio"]
    }

    return JSONResponse(status_code=200, content={'status': 'success', 'content': response})
