from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base

class user(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    activate = Column(Boolean, default=False)
    api_key = Column(String, unique=True, nullable=True)