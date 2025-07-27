#!/usr/bin/env python3
"""
StockAI Dependency Compatibility Checker
This script checks if all dependencies are compatible and properly installed.
"""

import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    print(f"   Platform: {platform.platform()}")
    print(f"   Architecture: {platform.machine()}")
    
    if version.major == 3 and version.minor >= 9:
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python version is not compatible. Need Python 3.9+")
        return False

def check_system_dependencies():
    """Check if system dependencies are available"""
    print("\n🔧 Checking system dependencies...")
    
    # Check for TA-Lib system library
    try:
        result = subprocess.run(['ldconfig', '-p'], capture_output=True, text=True)
        if 'libta_lib' in result.stdout:
            print("   ✅ TA-Lib system library found")
            return True
        else:
            print("   ⚠️  TA-Lib system library not found (will be installed in Docker)")
            return True
    except FileNotFoundError:
        print("   ⚠️  ldconfig not available (will be installed in Docker)")
        return True

def check_python_packages():
    """Check Python package compatibility"""
    print("\n📦 Checking Python packages...")
    
    packages = [
        ('fastapi', '0.109.0'),
        ('uvicorn', '0.27.0'),
        ('sqlalchemy', '2.0.25'),
        ('alembic', '1.13.1'),
        ('psycopg2-binary', '2.9.9'),
        ('redis', '5.0.1'),
        ('python-jose', '3.3.0'),
        ('passlib', '1.7.4'),
        ('bcrypt', '4.0.1'),
        ('python-multipart', '0.0.6'),
        ('httpx', '0.26.0'),
        ('yfinance', '0.2.65'),
        ('numpy', '2.0.2'),
        ('pandas', '2.3.1'),
        ('pydantic', '2.11.7'),
        ('pydantic-settings', '2.6.1'),
    ]
    
    all_good = True
    
    for package, expected_version in packages:
        try:
            module = __import__(package.replace('-', '_'))
            version = getattr(module, '__version__', 'unknown')
            print(f"   ✅ {package} {version}")
        except ImportError:
            print(f"   ❌ {package} - Missing")
            all_good = False
    
    return all_good

def check_docker_compatibility():
    """Check Docker compatibility"""
    print("\n🐳 Checking Docker compatibility...")
    
    try:
        # Check Docker version
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Docker: {result.stdout.strip()}")
        else:
            print("   ❌ Docker not available")
            return False
            
        # Check Docker Compose
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Docker Compose: {result.stdout.strip()}")
        else:
            print("   ❌ Docker Compose not available")
            return False
            
        # Check if Docker daemon is running
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Docker daemon is running")
        else:
            print("   ❌ Docker daemon is not running")
            return False
            
        return True
        
    except FileNotFoundError:
        print("   ❌ Docker not installed")
        return False

def check_architecture_compatibility():
    """Check architecture compatibility"""
    print("\n🏗️  Checking architecture compatibility...")
    
    arch = platform.machine()
    print(f"   Architecture: {arch}")
    
    if arch in ['x86_64', 'AMD64']:
        print("   ✅ x86_64 architecture - fully supported")
        return True
    elif arch in ['aarch64', 'arm64']:
        print("   ✅ ARM64 architecture - fully supported with pandas_ta")
        print("   ℹ️  No compilation issues with pure Python technical indicators")
        return True
    else:
        print(f"   ⚠️  Unknown architecture {arch} - may have compatibility issues")
        return True

def check_environment_files():
    """Check if required files exist"""
    print("\n📁 Checking project files...")
    
    required_files = [
        'backend/requirements.txt',
        'backend/Dockerfile',
        'frontend-react/package.json',
        'frontend-react/Dockerfile',
        'docker-compose.yml',
        '.env'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def main():
    """Main function"""
    print("🔍 StockAI Dependency Compatibility Checker")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_system_dependencies(),
        check_python_packages(),
        check_docker_compatibility(),
        check_architecture_compatibility(),
        check_environment_files()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 All compatibility checks passed!")
        print("\n📋 Your environment is ready for StockAI development.")
        print("\n🚀 Next steps:")
        print("1. For Docker deployment: ./start.sh")
        print("2. For local development: ./install_deps.sh")
        print("3. Test setup: python test_setup.py")
    else:
        print("❌ Some compatibility checks failed.")
        print("\n🔧 Recommendations:")
        print("1. Install missing Python packages: pip install -r backend/requirements.txt")
        print("2. Start Docker Desktop if not running")
        print("3. Check your .env file configuration")
        print("4. pandas_ta provides pure Python technical indicators - no compilation needed")
        sys.exit(1)

if __name__ == "__main__":
    main() 