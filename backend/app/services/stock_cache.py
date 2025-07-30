import redis
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from ..core.config import settings
from ..core.logger import logger

class StockCacheService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.cache_ttl = 24 * 60 * 60  # 24 hours in seconds
    
    def _get_user_cache_key(self, user_id: int, date: str) -> str:
        """Generate cache key for user's daily searches"""
        return f"stock_cache:user:{user_id}:date:{date}"
    
    def _get_stock_cache_key(self, user_id: int, symbol: str, date: str) -> str:
        """Generate cache key for specific stock data"""
        return f"stock_data:user:{user_id}:symbol:{symbol.upper()}:date:{date}"
    
    def _get_today_date(self) -> str:
        """Get today's date in YYYY-MM-DD format"""
        return datetime.utcnow().strftime("%Y-%m-%d")
    
    def _get_cache_expiry(self) -> int:
        """Get cache expiry time - expires at midnight UTC"""
        now = datetime.utcnow()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return int((tomorrow - now).total_seconds())
    
    def store_stock_analysis(self, user_id: int, symbol: str, analysis_data: Dict[str, Any]) -> bool:
        """Store stock analysis in cache"""
        try:
            date = self._get_today_date()
            cache_key = self._get_stock_cache_key(user_id, symbol, date)
            expiry = self._get_cache_expiry()
            
            # Store the analysis data
            self.redis_client.setex(
                cache_key,
                expiry,
                json.dumps(analysis_data)
            )
            
            # Add to user's daily search list
            user_cache_key = self._get_user_cache_key(user_id, date)
            search_entry = {
                "symbol": symbol.upper(),
                "timestamp": datetime.utcnow().isoformat(),
                "cache_key": cache_key
            }
            
            # Get existing searches or create new list
            existing_searches = self.get_todays_searches(user_id)
            if not existing_searches:
                existing_searches = []
            
            # Check if symbol already exists in today's searches
            symbol_exists = any(search["symbol"] == symbol.upper() for search in existing_searches)
            if not symbol_exists:
                existing_searches.append(search_entry)
                
                # Store updated search list
                self.redis_client.setex(
                    user_cache_key,
                    expiry,
                    json.dumps(existing_searches)
                )
            
            logger.info(f"Stored stock analysis for user {user_id}, symbol {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store stock analysis for user {user_id}, symbol {symbol}: {str(e)}", exc_info=True)
            return False
    
    def get_cached_analysis(self, user_id: int, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached stock analysis if available"""
        try:
            date = self._get_today_date()
            cache_key = self._get_stock_cache_key(user_id, symbol, date)
            
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                analysis_data = json.loads(cached_data)
                logger.info(f"Retrieved cached analysis for user {user_id}, symbol {symbol}")
                return analysis_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached analysis for user {user_id}, symbol {symbol}: {str(e)}", exc_info=True)
            return None
    
    def get_todays_searches(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all of today's searches for a user"""
        try:
            date = self._get_today_date()
            user_cache_key = self._get_user_cache_key(user_id, date)
            
            cached_searches = self.redis_client.get(user_cache_key)
            if cached_searches:
                searches = json.loads(cached_searches)
                logger.info(f"Retrieved {len(searches)} today's searches for user {user_id}")
                return searches
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get today's searches for user {user_id}: {str(e)}", exc_info=True)
            return []
    
    def get_todays_searches_with_data(self, user_id: int) -> List[Dict[str, Any]]:
        """Get today's searches with full analysis data"""
        try:
            searches = self.get_todays_searches(user_id)
            searches_with_data = []
            
            for search in searches:
                cache_key = search.get("cache_key")
                if cache_key:
                    cached_data = self.redis_client.get(cache_key)
                    if cached_data:
                        analysis_data = json.loads(cached_data)
                        search["analysis_data"] = analysis_data
                        searches_with_data.append(search)
            
            logger.info(f"Retrieved {len(searches_with_data)} searches with data for user {user_id}")
            return searches_with_data
            
        except Exception as e:
            logger.error(f"Failed to get today's searches with data for user {user_id}: {str(e)}", exc_info=True)
            return []
    
    def clear_user_cache(self, user_id: int) -> bool:
        """Clear all cached data for a user"""
        try:
            date = self._get_today_date()
            user_cache_key = self._get_user_cache_key(user_id, date)
            
            # Get all search entries
            searches = self.get_todays_searches(user_id)
            
            # Delete individual stock cache entries
            for search in searches:
                cache_key = search.get("cache_key")
                if cache_key:
                    self.redis_client.delete(cache_key)
            
            # Delete user's search list
            self.redis_client.delete(user_cache_key)
            
            logger.info(f"Cleared cache for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache for user {user_id}: {str(e)}", exc_info=True)
            return False

# Create service instance
stock_cache_service = StockCacheService() 