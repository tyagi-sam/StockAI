import secrets
import redis
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple

from ..core.config import settings
from ..core.logger import logger

class OTPService:
    def __init__(self):
        # Initialize Redis connection
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.otp_length = settings.OTP_LENGTH
        self.otp_expire_minutes = settings.OTP_EXPIRE_MINUTES
    
    def generate_otp(self) -> str:
        """Generate a random OTP"""
        return ''.join(secrets.choice('0123456789') for _ in range(self.otp_length))
    
    def _hash_otp(self, otp: str, salt: str) -> str:
        """Hash OTP with salt using SHA256"""
        return hashlib.sha256((otp + salt).encode()).hexdigest()
    
    def _generate_salt(self) -> str:
        """Generate a random salt for OTP hashing"""
        return secrets.token_hex(16)
    
    def _get_otp_key(self, email: str) -> str:
        """Get Redis key for OTP storage"""
        return f"otp:{email}"
    
    def _get_attempts_key(self, email: str) -> str:
        """Get Redis key for OTP attempts tracking"""
        return f"otp_attempts:{email}"
    
    def store_otp(self, email: str, otp: str) -> bool:
        """Store hashed OTP in Redis with expiration"""
        try:
            # Generate salt and hash the OTP
            salt = self._generate_salt()
            otp_hash = self._hash_otp(otp, salt)
            
            otp_data = {
                "otp_hash": otp_hash,  # Store hashed OTP instead of plain text
                "salt": salt,           # Store salt for verification
                "created_at": datetime.utcnow().isoformat(),
                "attempts": 0
            }
            
            key = self._get_otp_key(email)
            # Store OTP with expiration
            self.redis_client.setex(
                key,
                self.otp_expire_minutes * 60,  # Convert minutes to seconds
                json.dumps(otp_data)
            )
            
            logger.info(f"Hashed OTP stored for email: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store OTP for {email}: {str(e)}", exc_info=True)
            return False
    
    def get_otp(self, email: str) -> Optional[Tuple[str, str, datetime, int]]:
        """Get hashed OTP and salt from Redis"""
        try:
            key = self._get_otp_key(email)
            otp_data_str = self.redis_client.get(key)
            
            if not otp_data_str:
                return None
            
            otp_data = json.loads(otp_data_str)
            created_at = datetime.fromisoformat(otp_data["created_at"])
            attempts = otp_data.get("attempts", 0)
            
            # Return hashed OTP, salt, creation time, and attempts
            return otp_data["otp_hash"], otp_data["salt"], created_at, attempts
            
        except Exception as e:
            logger.error(f"Failed to get OTP for {email}: {str(e)}", exc_info=True)
            return None
    
    def verify_otp(self, email: str, provided_otp: str) -> Tuple[bool, str]:
        """Verify OTP and return success status and message"""
        try:
            # Get stored hashed OTP
            otp_result = self.get_otp(email)
            if not otp_result:
                return False, "OTP expired or not found"
            
            stored_otp_hash, salt, created_at, attempts = otp_result
            
            # Check if OTP has expired
            if datetime.utcnow() - created_at > timedelta(minutes=self.otp_expire_minutes):
                self.delete_otp(email)
                return False, "OTP has expired"
            
            # Check if too many attempts
            if attempts >= 5:
                self.delete_otp(email)
                return False, "Too many failed attempts. Please request a new OTP."
            
            # Hash the provided OTP with stored salt and compare
            provided_otp_hash = self._hash_otp(provided_otp, salt)
            
            if provided_otp_hash == stored_otp_hash:
                # OTP is correct, delete it
                self.delete_otp(email)
                logger.info(f"OTP verified successfully for email: {email}")
                return True, "OTP verified successfully"
            else:
                # Increment attempts
                self._increment_attempts(email)
                remaining_attempts = 5 - (attempts + 1)
                return False, f"Invalid OTP. {remaining_attempts} attempts remaining."
                
        except Exception as e:
            logger.error(f"Failed to verify OTP for {email}: {str(e)}", exc_info=True)
            return False, "Error verifying OTP"
    
    def _increment_attempts(self, email: str) -> None:
        """Increment OTP attempts counter"""
        try:
            key = self._get_otp_key(email)
            otp_data_str = self.redis_client.get(key)
            
            if otp_data_str:
                otp_data = json.loads(otp_data_str)
                otp_data["attempts"] = otp_data.get("attempts", 0) + 1
                
                # Update with remaining time
                ttl = self.redis_client.ttl(key)
                if ttl > 0:
                    self.redis_client.setex(key, ttl, json.dumps(otp_data))
                    
        except Exception as e:
            logger.error(f"Failed to increment attempts for {email}: {str(e)}", exc_info=True)
    
    def delete_otp(self, email: str) -> bool:
        """Delete OTP from Redis"""
        try:
            key = self._get_otp_key(email)
            self.redis_client.delete(key)
            logger.info(f"OTP deleted for email: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete OTP for {email}: {str(e)}", exc_info=True)
            return False
    
    def resend_otp(self, email: str) -> Tuple[bool, str]:
        """Resend OTP (delete old one and generate new one)"""
        try:
            # Delete existing OTP
            self.delete_otp(email)
            
            # Generate new OTP
            new_otp = self.generate_otp()
            
            # Store new OTP
            if self.store_otp(email, new_otp):
                logger.info(f"New OTP generated for email: {email}")
                return True, new_otp
            else:
                return False, "Failed to generate new OTP"
                
        except Exception as e:
            logger.error(f"Failed to resend OTP for {email}: {str(e)}", exc_info=True)
            return False, "Error resending OTP"
    
    def is_otp_valid(self, email: str) -> bool:
        """Check if OTP exists and is not expired"""
        try:
            otp_result = self.get_otp(email)
            if not otp_result:
                return False
            
            _, _, created_at, attempts = otp_result
            
            # Check if expired
            if datetime.utcnow() - created_at > timedelta(minutes=self.otp_expire_minutes):
                return False
            
            # Check if too many attempts
            if attempts >= 5:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check OTP validity for {email}: {str(e)}", exc_info=True)
            return False

# Create OTP service instance
otp_service = OTPService() 