#!/usr/bin/env python3
"""
Generate secure keys for production deployment
Run this script to generate JWT_SECRET and FERNET_KEY for your production environment
"""

import secrets
import base64
from cryptography.fernet import Fernet

def generate_jwt_secret(length=64):
    """Generate a secure JWT secret"""
    return secrets.token_urlsafe(length)

def generate_fernet_key():
    """Generate a Fernet key for encryption"""
    key = Fernet.generate_key()
    return key.decode('utf-8')

def generate_strong_password(length=32):
    """Generate a strong password for database/redis"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("🔐 Generating Production Security Keys")
    print("=" * 50)
    
    print("\n📝 Add these to your .env file on EC2:")
    print("-" * 40)
    
    print(f"\n# Database Password")
    print(f"POSTGRES_PASSWORD={generate_strong_password()}")
    
    print(f"\n# Redis Password") 
    print(f"REDIS_PASSWORD={generate_strong_password()}")
    
    print(f"\n# JWT Secret")
    print(f"JWT_SECRET={generate_jwt_secret()}")
    
    print(f"\n# Fernet Key (for encryption)")
    print(f"FERNET_KEY={generate_fernet_key()}")
    
    print("\n" + "=" * 50)
    print("⚠️  IMPORTANT: Keep these keys secure and never commit them to git!")
    print("💡 Copy these values to your .env file on EC2") 