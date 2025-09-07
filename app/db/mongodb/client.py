from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from core.configs import config

from typing import AsyncGenerator

client = AsyncMongoClient(config.mongodb_url, server_api=ServerApi('1'))
db = client[config.atlas_db_name]


async def get_db() -> AsyncGenerator:
    try:
        yield db
    finally:
        pass

async def close_client():
    client.close()
