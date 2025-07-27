from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for OAuth users

class UserUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict] = None

class UserResponse(UserBase):
    id: int
    is_email_verified: bool
    email_verified_at: Optional[datetime] = None
    daily_search_count: int
    last_search_reset: datetime
    preferences: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None 