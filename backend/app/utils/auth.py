"""
Authentication utilities for the Agno chatbot application.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import structlog

from app.config import settings

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password processing failed"
        )


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token creation failed"
        )


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Token processing error: {e}")
        return None


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a refresh token with longer expiration."""
    try:
        to_encode = data.copy()
        # Refresh tokens typically last 7 days
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Refresh token creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Refresh token creation failed"
        )


def generate_session_token() -> str:
    """Generate a unique session token."""
    import secrets
    return secrets.token_urlsafe(32)


def validate_password_strength(password: str) -> bool:
    """Validate password strength requirements."""
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False
    
    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return False
    
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return False
    
    return True


def sanitize_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize user data by removing sensitive fields."""
    sensitive_fields = {"password", "password_hash", "session_token"}
    return {k: v for k, v in user_data.items() if k not in sensitive_fields} 