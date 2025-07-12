from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.configs import config  # nanti kita buat config.py

DATABASE_URL = config.database_url  # contoh: "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
