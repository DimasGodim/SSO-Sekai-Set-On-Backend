from fastapi import FastAPI

from app.api import auth, api_key, user, weather, train, news, tts
from app.db.init_db import init
from app.service.nhk import start_news_fetcher
from app.middleware.api_logger import APILogMiddleware

app = FastAPI(
    title="Sekai Set On API",
    description="EZ Intergration with japanese platform (I HATE LOCK REGION) ",
    version="1.0.0"
)

# Inisialisasi database 
@app.on_event("startup")
def startup_event():
    init()
    start_news_fetcher()

# Router
app.include_router(auth.router, prefix="/auth", tags=["Autentication"])

app.include_router(news.router, prefix="/news", tags=["Japanese News"])

app.include_router(tts.router, prefix='/tts', tags=['Text To Sound'])

app.include_router(weather.router, prefix="/weather", tags=["Weather Information"])

app.include_router(train.router, prefix="/train", tags=["Train Information"])

app.include_router(api_key.router, prefix="/api-key", tags=["Api Key"])

app.include_router(user.router, prefix="/user", tags=["User"])

# Middleware
app.add_middleware(APILogMiddleware)