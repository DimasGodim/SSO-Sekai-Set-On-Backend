from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import verify_api_key

import requests
import re
import json

from pathlib import Path
from datetime import date as date_parameter, time as time_parameter
from bs4 import BeautifulSoup
from urllib.parse import quote

router = APIRouter()

def extract_routes_from_soup(soup):
    """Ekstrak data route dari BeautifulSoup object"""
    routes = []
    
    # Mencari semua route header untuk mendapatkan informasi dasar
    route_headers = soup.find_all('a', class_='route_header')
    
    for i, header in enumerate(route_headers, 1):
        route_data = {}
        
        # Ekstrak informasi dari header
        tbl = header.find('div', class_='tbl')
        if tbl:
            cols = tbl.find_all('div', class_='col')
            
            # Route number
            route_data['route_number'] = i
            
            # Time
            time_col = cols[1] if len(cols) > 1 else None
            if time_col:
                time_text = time_col.get_text(strip=True)
                if '→' in time_text:
                    departure, arrival = time_text.split('→')
                    route_data['departure_time'] = departure.strip()
                    route_data['arrival_time'] = arrival.strip()
            
            # Duration
            duration_col = cols[2] if len(cols) > 2 else None
            if duration_col:
                route_data['duration'] = duration_col.get_text(strip=True)
            
            # Fare
            fare_col = cols[3] if len(cols) > 3 else None
            if fare_col:
                route_data['fare'] = fare_col.get_text(strip=True)
            
            # Labels (Cheap, Fast, Easy)
            labels_col = cols[4] if len(cols) > 4 else None
            if labels_col:
                labels = labels_col.find_all('span', class_='label')
                route_data['labels'] = [label.get_text(strip=True) for label in labels]
            else:
                route_data['labels'] = []
        
        routes.append(route_data)
    
    # Extract detailed route information for the first route
    route_detail = soup.find('div', id='route1')
    if route_detail and routes:
        detail_data = extract_route_detail(route_detail)
        routes[0]['detailed_route'] = detail_data
    
    return routes

def extract_route_detail(route_block):
    """Ekstrak detail route lengkap dengan stasiun dan transfer"""
    detail = {
        'stations': [],
        'lines': [],
        'transfers': [],
        'total_fare': None
    }
    
    # Mencari semua baris stasiun
    station_rows = route_block.find_all('div', class_='row sta')
    line_rows = route_block.find_all('div', class_='row line')
    trans_rows = route_block.find_all('div', class_='row trans')
    
    # Ekstrak stasiun
    for row in station_rows:
        station_info = {}
        
        # Waktu
        time_elem = row.find(class_='time')
        if time_elem:
            station_info['time'] = time_elem.get_text(strip=True)
        
        # Nama stasiun bahasa Inggris
        name_main = row.find('p', id='eki_name_main')
        if name_main:
            # Clean station name (remove weather icons etc)
            station_name = name_main.get_text(strip=True)
            # Remove weather icon text if present
            station_info['name_en'] = re.sub(r'[^\w\s-]', '', station_name).strip()
        
        # Nama stasiun dalam bahasa Jepang
        name_sub = row.find('p', class_='lang_sub')
        if name_sub:
            station_info['name_jp'] = name_sub.get_text(strip=True)
        
        # Station code dari gambar
        img_elem = row.find('img', class_='icn_sta')
        if img_elem and 'alt' in img_elem.attrs:
            station_info['station_code'] = img_elem['alt']
        
        # Station type
        if 'from' in row.get('class', []):
            station_info['type'] = 'departure'
        elif 'to' in row.get('class', []):
            station_info['type'] = 'arrival'
        else:
            station_info['type'] = 'transit'
        
        detail['stations'].append(station_info)
    
    # Ekstrak informasi jalur kereta
    for row in line_rows:
        line_info = {}
        
        # Fare information
        fare_elem = row.find(class_='fare')
        if fare_elem:
            fare_text = fare_elem.get_text(strip=True)
            line_info['fare_info'] = fare_text
            
            # Extract fare amount
            fare_match = re.search(r'(\d+)\s*yen', fare_text)
            if fare_match and not detail['total_fare']:
                detail['total_fare'] = fare_match.group(1) + ' yen'
        
        # Line name English
        name_main = row.find('p', id='rosen_name_main')
        if name_main:
            line_info['line_name_en'] = name_main.get_text(strip=True)
        
        # Line name Japanese
        name_sub = row.find('p', class_='lang_sub')
        if name_sub:
            line_info['line_name_jp'] = name_sub.get_text(strip=True)
        
        # Duration
        aside_elem = row.find(class_='aside')
        if aside_elem:
            duration_text = aside_elem.get_text(strip=True)
            line_info['duration'] = duration_text
        
        # Train type
        tra_elem = row.find('p', class_='tra')
        if tra_elem:
            line_info['train_type'] = tra_elem.get_text(strip=True)
        
        detail['lines'].append(line_info)
    
    # Ekstrak informasi transfer
    for row in trans_rows:
        transfer_info = {}
        
        # Transfer details
        aside_elem = row.find(class_='aside')
        if aside_elem:
            transfer_text = aside_elem.get_text(strip=True)
            transfer_info['transfer_details'] = transfer_text
        
        detail['transfers'].append(transfer_info)
    
    return detail

@router.get('/schedule')
def schedule_train(
    from_station: str = Query(..., description="Departure station in romaji"),
    to_station: str = Query(..., description="Arrival station in romaji"),
    date: date_parameter = Query(..., description="Date in YYYY-MM-DD"),
    time: time_parameter = Query(..., description="Time in HH:MM"),
    db: Session = Depends(get_db),
    api_key=Depends(verify_api_key)
):
    url = "https://world.jorudan.co.jp/mln/en/"
    params = {
        "p": "0",
        "from": from_station,
        "to": to_station,
        "date": date.strftime("%m/%d/%Y"),
        "time": time.strftime("%H:%M"),
        "ft": "0",
        "ic": "0",
        "ut": "0",
        "up": "0",
        "us": "0",
        "nzm": "0",
        "nzm_mzh": "",
        "sub_lang": "ja"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://world.jorudan.co.jp/mln/en/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch train schedule (status code {response.status_code})"
            )
        
        soup = BeautifulSoup(response.content, 'html.parser')
        routes = extract_routes_from_soup(soup)

        if not routes:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "Not Found",
                    "data":{
                        "message": "No route found",
                        "from": from_station,
                        "to": to_station,
                        "date": date.isoformat(),
                        "time": time.strftime("%H:%M")
                    }
                }
            )

        data = {
            "from": from_station,
            "to": to_station,
            "date": date.isoformat(),
            "time": time.strftime("%H:%M"),
            "total_results": len(routes),
            "routes": routes
        }

        return JSONResponse(status_code=200, content={'status': 'success', 'data': data})

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Request failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get('/list')
def list_railway(
    city: str = Query(None), 
    prefektur: str = Query(None),
    db: Session = Depends(get_db), 
    api_key=Depends(verify_api_key)
):
    try:
        # Baca file JSON statis
        json_path = Path("app/static/stations_rail.json")
        with open(json_path, "r", encoding="utf-8") as f:
            stations = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load station data: {e}")
    
    # Filter berdasarkan city dan/atau prefektur jika diberikan
    filtered = []
    for station in stations:
        if city and station.get("city", "").lower() != city.lower():
            continue
        if prefektur and station.get("prefecture", "").lower() != prefektur.lower():
            continue
        filtered.append({
            "romaji": station.get("romaji"),
            "city": station.get("city"),
            "prefecture": station.get("prefecture"),
            "lat": station.get("lat"),
            "lon": station.get("lon")
        })

    return JSONResponse (status_code=200, content={'status': 'success', 'data': filtered})