from pydantic_settings import BaseSettings
from typing import Optional, List, Union
from pydantic import AnyHttpUrl, validator, field_validator
import secrets

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Stock AI"
    
    # Security
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Database
    DATABASE_URL: str
    POSTGRES_PASSWORD: Optional[str] = None
    
    # Redis
    REDIS_URL: str
    REDIS_PASSWORD: Optional[str] = None
    
    # Google OAuth (for user authentication)
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    
    # Zerodha (for stock data - using our API key)
    ZERODHA_API_KEY: str
    ZERODHA_API_SECRET: str
    
    # AI Analysis
    OPENAI_API_KEY: Optional[str] = None
    
    # Encryption
    FERNET_KEY: str  # Base64-encoded 32-byte key for encrypting sensitive data
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://frontend:3000"
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"
    
    # WebSocket
    WS_URL: str = "ws://localhost:8000"
    NEXT_PUBLIC_WS_URL: str = "ws://localhost:8000"
    
    class Config:
        case_sensitive = True
        env_file = "../.env"
        extra = "ignore"  # Allow extra fields in .env file

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Handle CORS origins as comma-separated string
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        
        # Validate required fields
        self._validate_required_fields()
    
    def _validate_required_fields(self):
        """Validate that all required fields are present"""
        required_fields = [
            'JWT_SECRET', 'DATABASE_URL', 'REDIS_URL', 
            'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET',
            'ZERODHA_API_KEY', 'ZERODHA_API_SECRET',
            'FERNET_KEY'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field, None):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
    
    @field_validator('JWT_SECRET')
    @classmethod
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError('JWT_SECRET must be at least 32 characters long')
        return v
    
    @field_validator('FERNET_KEY')
    @classmethod
    def validate_fernet_key(cls, v):
        if len(v) < 44:  # Base64 encoded 32-byte key
            raise ValueError('FERNET_KEY must be a valid base64-encoded 32-byte key')
        return v

settings = Settings() 