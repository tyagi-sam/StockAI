#!/usr/bin/env python3
"""
Script to generate a proper Fernet key for encryption.
Fernet keys must be 32 bytes long and base64-encoded.
"""

import base64
import os
from cryptography.fernet import Fernet

def generate_fernet_key():
    """Generate a new Fernet key"""
    key = Fernet.generate_key()
    return key.decode()

def validate_fernet_key(key_str):
    """Validate that a key string is a proper Fernet key"""
    try:
        # Try to create a Fernet instance with the key
        fernet = Fernet(key_str.encode())
        return True
    except Exception as e:
        print(f"Invalid Fernet key: {e}")
        return False

if __name__ == "__main__":
    print("Generating a new Fernet key...")
    new_key = generate_fernet_key()
    
    print(f"\nGenerated Fernet key: {new_key}")
    print(f"Key length: {len(new_key)} characters")
    
    # Validate the generated key
    if validate_fernet_key(new_key):
        print("✅ Key is valid!")
        
        print("\n📋 Add this to your .env file:")
        print(f"FERNET_KEY={new_key}")
        
        print("\n⚠️  Important:")
        print("- Keep this key secret and secure")
        print("- Use the same key across all instances of your application")
        print("- If you change this key, all encrypted data will become unreadable")
    else:
        print("❌ Generated key is invalid!") 