import requests
import re
from datetime import date, time
from bs4 import BeautifulSoup
from fastapi import HTTPException

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from datetime import date, time

def fetch_train_schedule(from_station: str, to_station: str, date: date, time: time):
    """Ambil data jadwal kereta dari Jorudan dengan headers & session lebih lengkap"""
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

    # Headers mirip browser sungguhan
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/114.0.0.0 Safari/537.36"),
        "Referer": "https://world.jorudan.co.jp/mln/en/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        # Preflight ke halaman utama → untuk dapat cookie/session
        try:
            session.get("https://world.jorudan.co.jp/mln/en/", timeout=8)
        except Exception:
            pass  # Kalau gagal tidak masalah, lanjutkan

        # Request utama
        resp = session.get(url, params=params, timeout=15, allow_redirects=True)

        # Retry sekali lagi jika 403
        if resp.status_code == 403:
            alt_headers = headers.copy()
            alt_headers.update({
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
            })
            resp = session.get(url, params=params, headers=alt_headers, timeout=15)

        if resp.status_code != 200:
            snippet = (resp.text or "")[:400].replace("\n", " ")
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Failed to fetch train schedule (status code {resp.status_code}). "
                       f"Response snippet: {snippet}"
            )

        soup = BeautifulSoup(resp.content, "html.parser")
        return soup

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")


def extract_routes_from_soup(soup: BeautifulSoup):
    """Ekstrak semua route dari soup HTML"""
    routes = []
    route_headers = soup.find_all("a", class_="route_header")
    for i, header in enumerate(route_headers, 1):
        route_data = {}
        tbl = header.find("div", class_="tbl")
        if tbl:
            cols = tbl.find_all("div", class_="col")
            route_data["route_number"] = i

            if len(cols) > 1:
                time_text = cols[1].get_text(strip=True)
                if "→" in time_text:
                    departure, arrival = time_text.split("→")
                    route_data["departure_time"] = departure.strip()
                    route_data["arrival_time"] = arrival.strip()

            if len(cols) > 2:
                route_data["duration"] = cols[2].get_text(strip=True)

            if len(cols) > 3:
                route_data["fare"] = cols[3].get_text(strip=True)

            if len(cols) > 4:
                labels = cols[4].find_all("span", class_="label")
                route_data["labels"] = [l.get_text(strip=True) for l in labels]
            else:
                route_data["labels"] = []

        routes.append(route_data)

    # detail route pertama
    route_detail = soup.find("div", id="route1")
    if route_detail and routes:
        routes[0]["detailed_route"] = extract_route_detail(route_detail)

    return routes


def extract_route_detail(route_block):
    """Ekstrak detail stasiun, jalur, transfer"""
    detail = {"stations": [], "lines": [], "transfers": [], "total_fare": None}
    station_rows = route_block.find_all("div", class_="row sta")
    line_rows = route_block.find_all("div", class_="row line")
    trans_rows = route_block.find_all("div", class_="row trans")

    for row in station_rows:
        station_info = {}
        time_elem = row.find(class_="time")
        if time_elem:
            station_info["time"] = time_elem.get_text(strip=True)

        name_main = row.find("p", id="eki_name_main")
        if name_main:
            station_info["name_en"] = re.sub(r"[^\w\s-]", "", name_main.get_text(strip=True)).strip()

        name_sub = row.find("p", class_="lang_sub")
        if name_sub:
            station_info["name_jp"] = name_sub.get_text(strip=True)

        img_elem = row.find("img", class_="icn_sta")
        if img_elem and "alt" in img_elem.attrs:
            station_info["station_code"] = img_elem["alt"]

        if "from" in row.get("class", []):
            station_info["type"] = "departure"
        elif "to" in row.get("class", []):
            station_info["type"] = "arrival"
        else:
            station_info["type"] = "transit"

        detail["stations"].append(station_info)

    for row in line_rows:
        line_info = {}
        fare_elem = row.find(class_="fare")
        if fare_elem:
            fare_text = fare_elem.get_text(strip=True)
            line_info["fare_info"] = fare_text
            if not detail["total_fare"]:
                match = re.search(r"(\d+)\s*yen", fare_text)
                if match:
                    detail["total_fare"] = match.group(1) + " yen"

        name_main = row.find("p", id="rosen_name_main")
        if name_main:
            line_info["line_name_en"] = name_main.get_text(strip=True)

        name_sub = row.find("p", class_="lang_sub")
        if name_sub:
            line_info["line_name_jp"] = name_sub.get_text(strip=True)

        aside_elem = row.find(class_="aside")
        if aside_elem:
            line_info["duration"] = aside_elem.get_text(strip=True)

        tra_elem = row.find("p", class_="tra")
        if tra_elem:
            line_info["train_type"] = tra_elem.get_text(strip=True)

        detail["lines"].append(line_info)

    for row in trans_rows:
        transfer_info = {}
        aside_elem = row.find(class_="aside")
        if aside_elem:
            transfer_info["transfer_details"] = aside_elem.get_text(strip=True)
        detail["transfers"].append(transfer_info)

    return detail