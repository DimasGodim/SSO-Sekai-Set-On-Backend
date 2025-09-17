from fastapi import APIRouter

from app.api.user.auth import router as auth_router
from app.api.user.manage import router as manage_router
from app.api.user.apikey import router as apikey_router
from app.api.service.news import router as news_router
from app.api.service.train import router as train_router
from app.api.service.tts import router as tts_router
from app.api.service.weather import router as weather_router

router = APIRouter(prefix="/api")

router.include_router(auth_router, prefix="/auth", tags=["User Auth"])
router.include_router(manage_router, prefix="/user", tags=["User Manage"])
router.include_router(apikey_router, prefix="/apikey", tags=["User API Key"])
router.include_router(news_router, prefix="/news", tags=["Service News"])
router.include_router(train_router, prefix="/train", tags=["Service Train"])
router.include_router(tts_router, prefix="/tts", tags=["Service TTS"])
router.include_router(weather_router, prefix="/weather", tags=["Service Weather"])