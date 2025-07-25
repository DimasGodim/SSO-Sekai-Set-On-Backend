from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from datetime import datetime

from app.db.database import Base

class user(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    nickname = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    activate = Column(Boolean, default=False)
    verification_code = Column(String, unique=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("user", backref="refresh_tokens")

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    link = Column(String, unique=True, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text)
    content = Column(Text)  
    source = Column(String, default="NHK")

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    expired = Column(DateTime, nullable=True)
    sequence = Column(Integer, nullable=False)

    usage_logs = relationship("APIUsageLog", back_populates="api_key")
    user = relationship("user", backref="api_keys")

class APIUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id", ondelete="CASCADE"))
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status_code = Column(Integer)

    api_key = relationship("APIKey", back_populates="usage_logs")
