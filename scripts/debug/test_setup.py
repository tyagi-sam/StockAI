#!/usr/bin/env python3
"""
Test Setup Script for StockAI Project
This script checks if the environment is properly configured.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.9+")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'alembic', 'psycopg2-binary',
        'redis', 'python-jose', 'passlib', 'bcrypt', 'python-multipart',
        'httpx', 'yfinance', 'numpy', 'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r backend/requirements.txt")
        return False
    
    return True

def check_environment():
    """Check if environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    # Add backend to path for imports
    backend_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_path))
    
    try:
        from app.core.config import settings
        print("✅ Environment configuration loaded successfully")
        
        # Check required settings
        required_settings = [
            'JWT_SECRET', 'DATABASE_URL', 'REDIS_URL', 
            'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET',
            'FERNET_KEY'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not getattr(settings, setting, None):
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"⚠️  Missing environment variables: {', '.join(missing_settings)}")
            print("Please check your .env file")
            return False
        else:
            print("✅ All required environment variables are set")
            return True
            
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        return False

def check_database():
    """Check if database is accessible"""
    print("\n🗄️  Checking database connection...")
    
    try:
        from app.db.session import async_engine
        from app.models import Base, User
        
        # Test connection
        import asyncio
        async def test_connection():
            async with async_engine.begin() as conn:
                await conn.run_sync(lambda sync_conn: sync_conn.execute("SELECT 1"))
        
        asyncio.run(test_connection())
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_redis():
    """Check if Redis is accessible"""
    print("\n🔴 Checking Redis connection...")
    
    try:
        import redis
        from app.core.config import settings
        
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("✅ Redis connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 StockAI Test Setup")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_environment(),
        check_database(),
        check_redis()
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("🎉 All checks passed! Your environment is ready.")
        print("\n📋 Next steps:")
        print("1. Start the backend: cd backend && python -m uvicorn app.main:app --reload")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 