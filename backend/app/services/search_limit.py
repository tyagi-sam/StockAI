from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Tuple

from ..models.user import User
from ..core.logger import logger

class SearchLimitService:
    DAILY_LIMIT = 10
    
    @staticmethod
    async def check_and_increment_search_count(user: User, db: AsyncSession) -> Tuple[bool, str, int]:
        """
        Check if user can search and increment their daily count.
        Returns: (can_search, message, remaining_searches)
        """
        try:
            # Initialize search count if it's None
            if user.daily_search_count is None:
                user.daily_search_count = 0
                await db.commit()
            
            # Check if we need to reset the daily count
            await SearchLimitService._reset_daily_count_if_needed(user, db)
            
            # Check if user has reached the limit
            if user.daily_search_count >= SearchLimitService.DAILY_LIMIT:
                return False, f"You have reached your daily limit of {SearchLimitService.DAILY_LIMIT} stock searches. Please try again tomorrow.", 0
            
            # Increment the search count
            user.daily_search_count += 1
            await db.commit()
            
            remaining = SearchLimitService.DAILY_LIMIT - user.daily_search_count
            return True, f"Search successful! You have {remaining} searches remaining today.", remaining
            
        except Exception as e:
            logger.error(f"Error checking search limit for user {user.id}: {str(e)}", exc_info=True)
            return False, "Error checking search limits", 0
    
    @staticmethod
    async def _reset_daily_count_if_needed(user: User, db: AsyncSession) -> None:
        """Reset daily search count if it's a new day"""
        try:
            now = datetime.utcnow()
            last_reset = user.last_search_reset or datetime.utcnow()
            
            # Check if it's a new day (different date)
            if now.date() > last_reset.date():
                user.daily_search_count = 0
                user.last_search_reset = now
                await db.commit()
                logger.info(f"Reset daily search count for user {user.id}")
                
        except Exception as e:
            logger.error(f"Error resetting daily count for user {user.id}: {str(e)}", exc_info=True)
    
    @staticmethod
    async def get_user_search_status(user: User, db: AsyncSession) -> dict:
        """Get user's current search status"""
        try:
            # Initialize search count if it's None
            if user.daily_search_count is None:
                user.daily_search_count = 0
                await db.commit()
            
            await SearchLimitService._reset_daily_count_if_needed(user, db)
            
            remaining = max(0, SearchLimitService.DAILY_LIMIT - user.daily_search_count)
            used = user.daily_search_count
            
            return {
                "daily_limit": SearchLimitService.DAILY_LIMIT,
                "used_today": used,
                "remaining_today": remaining,
                "can_search": remaining > 0,
                "last_reset": user.last_search_reset.isoformat() if user.last_search_reset else None
            }
            
        except Exception as e:
            logger.error(f"Error getting search status for user {user.id}: {str(e)}", exc_info=True)
            return {
                "daily_limit": SearchLimitService.DAILY_LIMIT,
                "used_today": 0,
                "remaining_today": SearchLimitService.DAILY_LIMIT,
                "can_search": True,
                "last_reset": None
            }
    
    @staticmethod
    async def reset_user_search_count(user: User, db: AsyncSession) -> bool:
        """Reset user's daily search count (admin function)"""
        try:
            user.daily_search_count = 0
            user.last_search_reset = datetime.utcnow()
            await db.commit()
            logger.info(f"Admin reset daily search count for user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting search count for user {user.id}: {str(e)}", exc_info=True)
            return False

# Create service instance
search_limit_service = SearchLimitService() 