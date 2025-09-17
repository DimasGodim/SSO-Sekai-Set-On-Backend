from fastapi import HTTPException

import json
import asyncio

from pathlib import Path
from typing import Optional
from configs import config

from data.db.sql.client import get_db as get_db_sql
from data.db.mongo.client import get_db as get_db_mongo

from data.act.sql.auth import (
    signup as signup_sql,
    cek_user as cek_user_sql,
    verification as verification_sql
)


from data.act.mongo.auth import (
    signup as signup_mongo,
    cek_user as cek_user_mongo,
    verification as verification_mongo
)

from data.act.mongo.access_token import (
    save_refresh_token as save_refresh_token_mongo,
    cek_refresh_token as cek_refresh_token_mongo,
    delete_refresh_token as delete_refresh_token_mongo
)

from data.act.sql.access_token import (
    save_refresh_token as save_refresh_token_sql,
    cek_refresh_token as cek_refresh_token_sql,
    delete_refresh_token as delete_refresh_token_sql
)

from data.act.sql.user import(
    get as get_user_sql,
    update as update_user_sql,
    delete as delete_user_sql
)


from data.act.mongo.user import(
    get as get_user_mongo,
    update as update_user_mongo,
    delete as delete_user_mongo
)


from data.act.sql.apikey import(
    information as information_apikey_sql,
    create as create_apikey_sql,
    delete as delete_apikey_sql,
    verification as verification_apikey_sql,
    save_log as save_log_apikey_sql
)


from data.act.mongo.apikey import(
    information as information_apikey_mongo,
    create as create_apikey_mongo,
    delete as delete_apikey_mongo,
    verification as verification_apikey_mongo,
    save_log as save_log_apikey_mongo
)


from data.act.sql.news import(
    save as save_news_sql,
    list as list_news_sql,
    search as search_news_sql
)


from data.act.mongo.news import(
    save as save_news_mongo,
    list as list_news_mongo,
    search as search_news_mongo
)
async def get_db():
    if config.mode_db == "sql":
        async for session in get_db_sql():
            yield session
    elif config.mode_db == "mongo":
        yield get_db_mongo()
db = None


# AUTENTIKASI
async def signup(data, verification_code):
    async for db in get_db():
        if config.mode_db == "sql":
            result = await signup_sql(data=data, verification_code=verification_code, db=db)
            return result
        elif config.mode_db == "mongo":
            result = await signup_mongo(data=data, verification_code=verification_code, db=db)
            return result

async def verification(data):
    async for db in get_db():
        if config.mode_db == "sql":
            result = await verification_sql(data=data, db=db)
            return result
        elif config.mode_db == "mongo":
            result = await verification_mongo(data=data, db=db)
            return result

async def cek_user(identification):
    async for db in get_db():
        if config.mode_db == "sql":
            result = await cek_user_sql(identification=identification, db=db)
            return result
        elif config.mode_db == "mongo":
            result = await cek_user_mongo(identification=identification, db=db)
            return result



# REFERSH TOKEN
async def save_refersh_token(token, email):
    async for db in get_db():
        if config.mode_db == "sql":
            await save_refresh_token_sql(token=token, email=email, db=db)
        elif config.mode_db == "mongo":
            await save_refresh_token_mongo(token=token, email=email, db=db)

async def cek_refersh_token(token, email):
    async for db in get_db():
        if config.mode_db == "sql":
            await cek_refresh_token_sql(token=token, email=email, db=db)
        elif config.mode_db == "mongo":
            await cek_refresh_token_mongo(token=token, email=email, db=db)

async def delete_refersh_token(token, email):
    async for db in get_db():
        if config.mode_db == "sql":
            await delete_refresh_token_sql(token=token, email=email, db=db)
        elif config.mode_db == "mongo":
            await delete_refresh_token_mongo(token=token, email=email, db=db)



# USER MANAGE
async def get_user(email):
    async for db in get_db():
        if config.mode_db == "sql":
            result = await get_user_sql(db=db, email=email)
            return result
        elif config.mode_db == "mongo":
            result = await get_user_mongo(db=db, email=email)
            return result

async def edit_user(email, data):
    async for db in get_db():
        if config.mode_db == "sql":
            result = await update_user_sql(data=data, email=email, db=db)
            return result
        elif config.mode_db == "mongo":
            result = await update_user_mongo(data=data, email=email, db=db)
            return result

async def delete_user(email):
    async for db in get_db():
        if config.mode_db == "sql":
            await delete_user_sql(email=email, db=db)
        elif config.mode_db == "mongo":
            await delete_user_mongo(email=email, db=db)



# APIKey
async def information_api_key(email):
    async for db in get_db():
        if config.mode_db == "sql":
            result = await information_apikey_sql(email=email, db=db)
            return result
        elif config.mode_db == "mongo":
            result = await information_apikey_mongo(email=email, db=db)
            return result

async def create_api_key(email, data):
    async for db in get_db():
        if config.mode_db == "sql":
            result = await create_apikey_sql(email=email, db=db, data=data)
            return result
        elif config.mode_db == "mongo":
            result = await create_apikey_mongo(db=db, data=data, email=email)
            return result
        
async def delete_api_key(title, email):
    async for db in get_db():
        if config.mode_db == "sql":
            await delete_apikey_sql(title=title, email=email, db=db)
        elif config.mode_db == "mongo":
            await delete_apikey_mongo(title=title, email=email, db=db)

async def verification_api_key(key):
    async for db in get_db():
        if config.mode_db == "sql":
            await verification_apikey_sql(key=key, db=db)
        elif config.mode_db == "mongo":
            await verification_apikey_mongo(key=key, db=db)

async def save_log_api_key(data):
    data=data.model_dump()
    async for db in get_db():
        if config.mode_db == "sql":
            await save_log_apikey_sql(data=data, db=db)
        elif config.mode_db == "mongo":
            await save_log_apikey_mongo(data=data, db=db)



# NEWS MANAGE
async def save_news(data):
    async for db in get_db():
        if config.mode_db == "sql":
            await save_news_sql(data=data, db=db)
        elif config.mode_db == "mongo":
            await save_news_mongo(data=data, db=db)

async def news_list():
    async for db in get_db():
        if config.mode_db == "sql":
            result = await list_news_sql(db=db)
            return result
        elif config.mode_db == "mongo":
            result = await list_news_mongo(db=db)
            return result
    
async def news_search(titile):
    async for db in get_db():
        if config.mode_db == "sql":
            await search_news_sql(title=titile, db=db)
        elif config.mode_db == "mongo":
            await search_news_mongo(title=titile, db=db)



# TRAIN MANAGE
def station(city: Optional[str] = None, prefektur: Optional[str] = None):
    try:
        json_path = Path("data/static/stations_rail.json")
        with open(json_path, "r", encoding="utf-8") as f:
            stations = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load station data: {e}")
    
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

    return filtered

# TTS MANAGE
def char():
    try:
        file_path = Path("data/static/character.json")
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

    return result