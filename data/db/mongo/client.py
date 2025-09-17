from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from configs import config

client = AsyncMongoClient(config.atlas_url, server_api=ServerApi('1'))
db = client[config.atlas_db_name]

def get_db():
    return db

def close_client():
    client.close()