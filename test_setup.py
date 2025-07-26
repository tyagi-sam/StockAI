#!/usr/bin/env python3
"""
Simple test script to verify the basic setup of the Stock AI application.
Run this script to check if all components are properly configured.
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test backend imports
        sys.path.append(str(Path(__file__).parent / "backend"))
        
        from app.core.config import settings
        print("✓ Config module imported successfully")
        
        from app.core.logger import logger
        print("✓ Logger module imported successfully")
        
        from app.models import Base, User, Trade
        print("✓ Models imported successfully")
        
        from app.db.session import get_db
        print("✓ Database session imported successfully")
        
        from app.services.zerodha import zerodha_service
        print("✓ Zerodha service imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\nTesting environment variables...")
    
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL", 
        "JWT_SECRET",
        "ZERODHA_API_KEY",
        "ZERODHA_API_SECRET",
        "FERNET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"✗ Missing: {var}")
        else:
            print(f"✓ Found: {var}")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    
    return True

def test_docker_files():
    """Test if Docker files exist"""
    print("\nTesting Docker files...")
    
    docker_files = [
        "docker-compose.yml",
        "backend/Dockerfile", 
        "frontend/Dockerfile"
    ]
    
    missing_files = []
    for file_path in docker_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"✗ Missing: {file_path}")
        else:
            print(f"✓ Found: {file_path}")
    
    if missing_files:
        print(f"\n⚠️  Missing Docker files: {', '.join(missing_files)}")
        return False
    
    return True

def test_frontend_files():
    """Test if frontend files exist"""
    print("\nTesting frontend files...")
    
    frontend_files = [
        "frontend/package.json",
        "frontend/src/app/page.tsx",
        "frontend/src/components/LoginForm.tsx",
        "frontend/src/components/StockAnalysis.tsx"
    ]
    
    missing_files = []
    for file_path in frontend_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"✗ Missing: {file_path}")
        else:
            print(f"✓ Found: {file_path}")
    
    if missing_files:
        print(f"\n⚠️  Missing frontend files: {', '.join(missing_files)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Stock AI Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_docker_files,
        test_frontend_files
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results")
    print("=" * 50)
    
    if all(results):
        print("🎉 All tests passed! Your setup looks good.")
        print("\nNext steps:")
        print("1. Copy env.example to .env and fill in your credentials")
        print("2. Run: docker-compose up -d")
        print("3. Access the application at http://localhost:3000")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install Python dependencies: pip install -r backend/requirements.txt")
        print("- Set up environment variables in .env file")
        print("- Ensure all files are in the correct locations")

if __name__ == "__main__":
    main() 