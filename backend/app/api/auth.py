"""
Authentication API endpoints for the Agno chatbot application.
"""

from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from app.models.user import UserCreate, UserLogin, UserProfile
from app.services.auth_service import AuthService
from app.utils.auth import verify_token

logger = structlog.get_logger()

router = APIRouter()
security = HTTPBearer()

# Initialize auth service
auth_service = AuthService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token."""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/signup", response_model=Dict[str, Any])
async def signup(user_data: UserCreate, request: Request):
    """Register a new user."""
    try:
        # Get client IP and user agent
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        result = await auth_service.register_user(user_data)
        
        logger.info(f"New user registered: {user_data.email} from IP: {client_ip}")
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": result["user_id"],
                "username": result["username"],
                "email": result["email"]
            },
            "tokens": {
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "token_type": result["token_type"]
            }
        }
        
    except ValueError as e:
        logger.warning(f"Signup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=Dict[str, Any])
async def login(login_data: UserLogin, request: Request):
    """Authenticate and login a user."""
    try:
        # Get client IP and user agent
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        result = await auth_service.login_user(login_data, client_ip, user_agent)
        
        logger.info(f"User logged in: {login_data.email} from IP: {client_ip}")
        
        return {
            "message": "Login successful",
            "user": {
                "id": result["user_id"],
                "username": result["username"],
                "email": result["email"]
            },
            "tokens": {
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "session_token": result["session_token"],
                "token_type": result["token_type"]
            }
        }
        
    except ValueError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("/logout")
async def logout(request: Request):
    """Logout a user by invalidating their session."""
    try:
        # Get session token from header or body
        session_token = request.headers.get("X-Session-Token")
        if not session_token:
            # Try to get from request body
            body = await request.json()
            session_token = body.get("session_token")
        
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session token is required"
            )
        
        success = await auth_service.logout_user(session_token)
        
        if success:
            logger.info(f"User logged out successfully")
            return {"message": "Logout successful"}
        else:
            logger.warning(f"Logout failed: session not found")
            return {"message": "Session not found or already inactive"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed. Please try again."
        )


@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(request: Request):
    """Refresh an access token using a refresh token."""
    try:
        # Get refresh token from request body
        body = await request.json()
        refresh_token = body.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
        result = await auth_service.refresh_token(refresh_token)
        
        logger.info("Token refreshed successfully")
        
        return {
            "message": "Token refreshed successfully",
            "tokens": {
                "access_token": result["access_token"],
                "token_type": result["token_type"]
            }
        }
        
    except ValueError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please try again."
        )


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile."""
    try:
        return {
            "message": "User profile retrieved successfully",
            "user": current_user
        }
        
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.get("/sessions", response_model=Dict[str, Any])
async def get_user_sessions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all active sessions for the current user."""
    try:
        user_id = current_user["id"]
        sessions = await auth_service.get_user_sessions(user_id)
        
        return {
            "message": "User sessions retrieved successfully",
            "sessions": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Get user sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user sessions"
        )


@router.post("/validate-session")
async def validate_session(request: Request):
    """Validate if a session token is active."""
    try:
        # Get session token from header or body
        session_token = request.headers.get("X-Session-Token")
        if not session_token:
            # Try to get from request body
            body = await request.json()
            session_token = body.get("session_token")
        
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session token is required"
            )
        
        is_valid = await auth_service.validate_session(session_token)
        
        return {
            "valid": is_valid,
            "message": "Session is valid" if is_valid else "Session is invalid or expired"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session validation failed"
        )


@router.post("/cleanup-sessions")
async def cleanup_expired_sessions():
    """Clean up expired sessions (admin endpoint)."""
    try:
        count = await auth_service.cleanup_expired_sessions()
        
        return {
            "message": f"Cleaned up {count} expired sessions",
            "cleaned_count": count
        }
        
    except Exception as e:
        logger.error(f"Session cleanup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session cleanup failed"
        ) 