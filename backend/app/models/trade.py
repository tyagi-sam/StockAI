from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base, TimestampMixin

class TradeSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradeStatus(str, enum.Enum):
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class Trade(Base, TimestampMixin):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    zerodha_order_id = Column(String, unique=True, index=True)
    symbol = Column(String, nullable=False)
    side = Column(Enum(TradeSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(Enum(TradeStatus), default=TradeStatus.OPEN)
    executed_at = Column(DateTime, nullable=False)
    trigger_price = Column(Float, nullable=True)
    
    # Foreign keys
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    leader = relationship("User", foreign_keys=[leader_id], back_populates="trades")
    follower = relationship("User", foreign_keys=[follower_id], back_populates="followed_trades") 