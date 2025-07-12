from fastapi import FastAPI
from app.api import auth
from app.db.init_db import init

app = FastAPI(
    title="Sekai Set On API",
    description="EZ Intergration with japanese platform (I HATE LOCK REGION) ",
    version="1.0.0"
)

# Inisialisasi database 
@app.on_event("startup")
def startup_event():
    init()

# Router
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
