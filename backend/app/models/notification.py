from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # 'trade', 'system', 'alert', etc.
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    data = Column(JSON, nullable=True)  # Additional data for the notification
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class NotificationPreference(Base, TimestampMixin):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    trade_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    alert_notifications = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences") 