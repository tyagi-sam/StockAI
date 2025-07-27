from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timedelta
import httpx
import os
import secrets

from ...db.session import get_db
from ...core.config import settings
from ...core.auth import create_access_token, get_current_user
from ...core.security import get_password_hash, verify_password
from ...models.user import User
from ...core.logger import logger
from ...services.email import email_service
from ...services.otp import otp_service

router = APIRouter()

class LoginRequest:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

class UserCreate:
    def __init__(self, email: str, password: str, name: str):
        self.email = email
        self.password = password
        self.name = name

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password"""
    try:
        logger.info(f"Login attempt for email: {form_data.username}")
        
        # Find user by email
        result = await db.execute(select(User).where(User.email == form_data.username))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(form_data.password, user.password):
            logger.warning(f"Failed login attempt for email: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {form_data.username}")
            raise HTTPException(status_code=400, detail="Inactive user")
        
        # Check if email is verified (only for manual registration, not OAuth)
        # Temporarily disabled for existing users - will be enabled once email service is configured
        # if user.password and not user.is_email_verified:
        #     logger.warning(f"Login attempt for unverified email: {form_data.username}")
        #     raise HTTPException(status_code=400, detail="Please verify your email before logging in")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        logger.info(f"Successful login for user: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_email_verified": user.is_email_verified
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/register")
async def register(
    user_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Register new user with email and password"""
    try:
        email = user_data.get("email")
        password = user_data.get("password")
        name = user_data.get("name")
        
        logger.info(f"Registration attempt for email: {email}")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {email}")
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create new user (not verified yet)
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            password=hashed_password,
            name=name,
            is_active=True,
            is_email_verified=False  # Email not verified initially
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Generate and send OTP
        otp = otp_service.generate_otp()
        if otp_service.store_otp(email, otp):
            # Send verification email
            if email_service.send_verification_otp(email, otp, name):
                logger.info(f"Verification OTP sent to: {email}")
                return {
                    "message": "Registration successful. Please check your email for verification code.",
                    "user": {
                        "id": new_user.id,
                        "email": new_user.email,
                        "name": new_user.name,
                        "is_email_verified": False
                    }
                }
            else:
                # Email failed, but user was created
                logger.error(f"Failed to send verification email to: {email}")
                return {
                    "message": "Registration successful, but verification email failed to send. Please contact support.",
                    "user": {
                        "id": new_user.id,
                        "email": new_user.email,
                        "name": new_user.name,
                        "is_email_verified": False
                    }
                }
        else:
            # OTP storage failed
            logger.error(f"Failed to store OTP for: {email}")
            raise HTTPException(status_code=500, detail="Failed to generate verification code")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/verify-email")
async def verify_email(
    verification_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Verify email with OTP"""
    try:
        email = verification_data.get("email")
        otp = verification_data.get("otp")
        
        if not email or not otp:
            raise HTTPException(status_code=400, detail="Email and OTP are required")
        
        logger.info(f"Email verification attempt for: {email}")
        
        # Verify OTP
        is_valid, message = otp_service.verify_otp(email, otp)
        
        if not is_valid:
            logger.warning(f"Invalid OTP for email: {email}")
            raise HTTPException(status_code=400, detail=message)
        
        # Find user and mark as verified
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User not found for email verification: {email}")
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.is_email_verified:
            logger.info(f"Email already verified for: {email}")
            return {"message": "Email already verified"}
        
        # Mark email as verified
        user.is_email_verified = True
        user.email_verified_at = datetime.utcnow()
        await db.commit()
        
        # Send welcome email
        email_service.send_welcome_email(email, user.name)
        
        # Generate JWT token for automatic login
        access_token = create_access_token(data={"sub": str(user.id)})
        
        logger.info(f"Email verified successfully for: {email}")
        
        return {
            "message": "Email verified successfully! Welcome to StockAI!",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_email_verified": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/resend-otp")
async def resend_otp(
    resend_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Resend verification OTP"""
    try:
        email = resend_data.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        logger.info(f"OTP resend request for: {email}")
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"OTP resend for non-existent user: {email}")
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.is_email_verified:
            logger.info(f"OTP resend for already verified email: {email}")
            return {"message": "Email already verified"}
        
        # Generate and send new OTP
        success, new_otp = otp_service.resend_otp(email)
        
        if success:
            if email_service.send_verification_otp(email, new_otp, user.name):
                logger.info(f"New OTP sent to: {email}")
                return {"message": "New verification code sent to your email"}
            else:
                logger.error(f"Failed to send new OTP email to: {email}")
                raise HTTPException(status_code=500, detail="Failed to send verification email")
        else:
            logger.error(f"Failed to generate new OTP for: {email}")
            raise HTTPException(status_code=500, detail="Failed to generate verification code")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP resend error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/login/google")
async def get_google_login_url():
    """Get Google OAuth login URL"""
    try:
        # Google OAuth configuration
        google_client_id = settings.GOOGLE_CLIENT_ID
        redirect_uri = f"{settings.FRONTEND_URL}/auth/callback"
        
        if not google_client_id:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        
        # Store state in session/cache for verification
        # For now, we'll use a simple approach
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={google_client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile&"
            f"state={state}"
        )
        
        logger.info("Generated Google login URL")
        
        return {"login_url": google_auth_url, "state": state}
        
    except Exception as e:
        logger.error(f"Error generating Google login URL: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate login URL")

@router.post("/callback/google")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Get parameters from request body
        body = await request.json()
        code = body.get("code")
        state = body.get("state")
        
        if not code:
            raise HTTPException(status_code=422, detail="Authorization code is required")
        
        logger.info(f"Google callback received for code: {code[:10]}...")
        
        # Exchange code for tokens
        google_client_id = settings.GOOGLE_CLIENT_ID
        google_client_secret = settings.GOOGLE_CLIENT_SECRET
        redirect_uri = f"{settings.FRONTEND_URL}/auth/callback"
        
        if not google_client_id or not google_client_secret:
            logger.error("Google OAuth credentials not configured")
            raise HTTPException(status_code=500, detail="Google OAuth not properly configured")
        
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
        
        # Get user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        async with httpx.AsyncClient() as client:
            user_response = await client.get(user_info_url, headers=headers)
            user_response.raise_for_status()
            user_info = user_response.json()
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == user_info.get("email")))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user (OAuth users are automatically verified)
            user = User(
                email=user_info.get("email"),
                name=user_info.get("name"),
                is_active=True,
                is_email_verified=True,  # OAuth emails are pre-verified
                email_verified_at=datetime.utcnow()
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Created new user from Google: {user.email}")
        else:
            # Update existing user info
            user.name = user_info.get("name")
            user.is_email_verified = True  # Ensure OAuth users are verified
            user.email_verified_at = datetime.utcnow()
            await db.commit()
            logger.info(f"Updated user from Google: {user.email}")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_email_verified": user.is_email_verified
            }
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in Google callback: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Google API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process Google callback")

@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        logger.info(f"Token refresh for user: {current_user.email}")
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(current_user.id)}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to refresh token")

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    try:
        logger.info(f"User info requested for: {current_user.email}")
        
        return {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "is_active": current_user.is_active,
            "is_email_verified": current_user.is_email_verified
        } 
        
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get user information") 