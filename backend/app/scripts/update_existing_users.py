#!/usr/bin/env python3
"""
Script to update existing users with default search limit values
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import async_engine
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

async def update_existing_users():
    """Update existing users with default search limit values"""
    async with AsyncSession(async_engine) as db:
        try:
            # Get all users
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            updated_count = 0
            
            for user in users:
                # Check if user needs initialization
                if user.daily_search_count is None:
                    user.daily_search_count = 0
                    updated_count += 1
                
                if user.last_search_reset is None:
                    user.last_search_reset = datetime.utcnow()
                    updated_count += 1
            
            if updated_count > 0:
                await db.commit()
                print(f"✅ Updated {updated_count} fields for existing users")
            else:
                print("✅ All users already have proper search limit values")
                
        except Exception as e:
            print(f"❌ Error updating users: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(update_existing_users()) 