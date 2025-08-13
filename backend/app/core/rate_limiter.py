from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Create rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
RATE_LIMITS = {
    "public": {
        "auth": "5/minute",      # Login attempts
        "health": "120/minute",  # Health checks (2 per second for docker health checks)
        "general": "10/minute"   # General endpoints
    },
    "authenticated": {
        "search": "3/minute",    # Stock searches
        "api": "20/minute",      # General API calls
        "heavy": "1/minute"      # Heavy operations
    },
    "admin": {
        "admin": "50/minute"     # Admin operations
    }
}

def get_rate_limit_for_user(request: Request, endpoint_type: str = "general") -> str:
    """
    Get appropriate rate limit based on user authentication status
    """
    # Check if user is authenticated
    user = getattr(request.state, "user", None)
    
    if user:
        # Check if user is admin (you can add admin role check here)
        if hasattr(user, 'is_admin') and user.is_admin:
            return RATE_LIMITS["admin"].get(endpoint_type, "50/minute")
        else:
            return RATE_LIMITS["authenticated"].get(endpoint_type, "20/minute")
    else:
        return RATE_LIMITS["public"].get(endpoint_type, "10/minute")

def rate_limit_by_user(endpoint_type: str = "general"):
    """
    Decorator for rate limiting based on user authentication status
    """
    def decorator(func):
        def wrapper(request: Request, *args, **kwargs):
            limit = get_rate_limit_for_user(request, endpoint_type)
            return limiter.limit(limit)(func)(request, *args, **kwargs)
        return wrapper
    return decorator

def get_client_ip(request: Request) -> str:
    """
    Get client IP address considering proxy headers
    """
    # Check for X-Forwarded-For header (set by nginx)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    # Fallback to direct IP
    return request.client.host if request.client else "unknown"

def log_rate_limit_violation(request: Request, endpoint: str):
    """
    Log rate limit violations for monitoring
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "Unknown")
    
    logger.warning(
        f"Rate limit violation - IP: {client_ip}, "
        f"Endpoint: {endpoint}, "
        f"User-Agent: {user_agent}"
    )

# Rate limit exceeded handler
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded
    """
    log_rate_limit_violation(request, request.url.path)
    
    return {
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "retry_after": exc.retry_after
    } 