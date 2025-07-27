from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)  # Nullable for OAuth users
    name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)  # Email verification status
    email_verified_at = Column(DateTime, nullable=True)  # When email was verified
    daily_search_count = Column(Integer, default=0, nullable=False)  # Daily stock search count
    last_search_reset = Column(DateTime, default=datetime.utcnow, nullable=False)  # When search count was last reset
    preferences = Column(JSON, nullable=True)  # JSON for user preferences 
