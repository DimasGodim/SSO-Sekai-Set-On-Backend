from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.core.deps import verify_api_key

import requests

router = APIRouter()

@router.get("/weather")
def get_weather(
    city: str = Query(...),
    db: Session = Depends(get_db),
    api_key=Depends(verify_api_key)
):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&country=japan"
    geo_response = requests.get(geo_url)
    if geo_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to find city coordinates")

    geo_data = geo_response.json()
    results = geo_data.get("results")
    if not results:
        raise HTTPException(status_code=404, detail="Cities not found in Japan")

    lat = results[0]["latitude"]
    lon = results[0]["longitude"]
    matched_name = results[0]["name"]

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_min,temperature_2m_max,weathercode&timezone=Asia%2FTokyo"

    try:
        response = requests.get(url)
        data = response.json()
        daily = data.get("daily", {})

        result = {
            "city": matched_name,
            "forecast": []
        }

        for i in range(len(daily["time"])):
            result["forecast"].append({
                "date": daily["time"][i],
                "temperature_min": daily["temperature_2m_min"][i],
                "temperature_max": daily["temperature_2m_max"][i],
                "weather_code": daily["weathercode"][i]
            })

        return JSONResponse(content={"status": "success", "data": result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve weather data: {str(e)}")
