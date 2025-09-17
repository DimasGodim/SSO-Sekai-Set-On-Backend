from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship

from datetime import datetime, timezone

from data.db.sql.client import Base

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    nickname = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    activate = Column(Boolean, default=False)
    verification_code = Column(String, unique=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    email = Column(String, ForeignKey("users.email", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expired = Column(DateTime(timezone=True))
    user = relationship("User", backref="refresh_tokens")

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    link = Column(String, unique=True, nullable=False)
    published_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    summary = Column(Text)
    content = Column(Text)  

class APIKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, unique=True, index=True, nullable=False, primary_key=True)
    title = Column(String, nullable=False)
    detail = Column(String, nullable=True)
    email = Column(String, ForeignKey("users.email", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expired = Column(DateTime(timezone=True), nullable=True)

    usage_logs = relationship("APIUsageLog", back_populates="api_key")
    user = relationship("User", backref="api_keys")

class APIUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, ForeignKey("api_keys.key", ondelete="CASCADE"))
    endpoint = Column(String, nullable=False)
    response_time = Column(Float, nullable=True)
    method = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    status_code = Column(Integer)

    api_key = relationship("APIKey", back_populates="usage_logs")
