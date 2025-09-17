from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from configs import config

from app.middleware.logger import APILogMiddleware

from app.service.nhk import start_news_fetcher

from data.db.sql.init import init

from data.db.mongo.client import close_client

from app.api.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    if config.mode_db == "sql":
        await init()

    await start_news_fetcher()
    
    yield
    if config.mode_db == "mongo":
        await close_client()


app = FastAPI(
    title="Sekai Set On API",
    description="EZ Intergration with japanese platform (I HATE LOCK REGION) ",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)
app.add_middleware(APILogMiddleware)

@app.get("/")
def check():
    return JSONResponse (status_code=200, content={"status": "ok", "message": "yeah im still alive"})

app.include_router(router)