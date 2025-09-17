from fastapi import APIRouter, Header, Query

from typing import Optional
from datetime import date as date_parameter, time as time_parameter

from data.act.base import station, verification_api_key

from app.schema.response.success import success as success_response
from app.service.train import fetch_train_schedule, extract_routes_from_soup, extract_route_detail

router = APIRouter()

@router.get("/station")
async def get_station(api_key: str = Header(...)):
    await verification_api_key(key=api_key)
    result = station()
    return success_response(data=result)
    
@router.get("/train_schedule")
async def schedule_train(
    from_station: str = Query(..., description="Departure station in romaji"),
    to_station: str = Query(..., description="Arrival station in romaji"),
    date: date_parameter = Query(..., description="Date in YYYY-MM-DD"),
    time: time_parameter = Query(..., description="Time in HH:MM"),
    api_key: str = Header(...),
):
    await verification_api_key(key=api_key)
    soup = fetch_train_schedule(from_station, to_station, date, time)
    routes = extract_routes_from_soup(soup)
    return success_response(data=routes)