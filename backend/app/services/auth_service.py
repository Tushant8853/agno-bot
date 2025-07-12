"""
Authentication service for the Agno chatbot application.
"""

import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import structlog

from app.config import settings
from app.models.user import User, UserCreate, UserLogin, UserSession
from app.utils.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    generate_session_token,
    validate_password_strength,
    sanitize_user_data
)

logger = structlog.get_logger()

# Database setup
Base = declarative_base()

class UserDB(Base):
    """Database model for users."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="user")
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    preferences = Column(Text)  # JSON string
    user_metadata = Column(Text)  # JSON string


class UserSessionDB(Base):
    """Database model for user sessions."""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String)
    user_agent = Column(String)
    session_metadata = Column(Text)  # JSON string


class AuthService:
    """Authentication service for user management."""
    
    def __init__(self):
        """Initialize the authentication service."""
        self.engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info("Authentication service initialized")
    
    def get_db(self) -> Session:
        """Get database session."""
        db = self.SessionLocal()
        try:
            return db
        except Exception as e:
            db.close()
            raise e
    
    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user."""
        db = None
        try:
            # Validate password strength
            if not validate_password_strength(user_data.password):
                raise ValueError("Password does not meet strength requirements")
            
            db = self.get_db()
            
            # Check if user already exists
            existing_user = db.query(UserDB).filter(
                (UserDB.email == user_data.email) | (UserDB.username == user_data.username)
            ).first()
            
            if existing_user:
                raise ValueError("User with this email or username already exists")
            
            # Create new user
            user_id = str(uuid.uuid4())
            password_hash = get_password_hash(user_data.password)
            
            new_user = UserDB(
                id=user_id,
                username=user_data.username,
                email=user_data.email,
                password_hash=password_hash,
                role="user",
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Create access token
            access_token = create_access_token(
                data={"sub": user_id, "email": user_data.email, "username": user_data.username}
            )
            
            # Create refresh token
            refresh_token = create_refresh_token(
                data={"sub": user_id, "email": user_data.email}
            )
            
            logger.info(f"User registered successfully: {user_data.email}")
            
            return {
                "user_id": user_id,
                "username": user_data.username,
                "email": user_data.email,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
            
        except ValueError as e:
            logger.warning(f"User registration failed: {e}")
            raise
        except Exception as e:
            logger.error(f"User registration error: {e}")
            raise
        finally:
            if db:
                db.close()
    
    async def login_user(self, login_data: UserLogin, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate and login a user."""
        try:
            db = self.get_db()
            
            # Find user by email
            user = db.query(UserDB).filter(UserDB.email == login_data.email).first()
            
            if not user:
                raise ValueError("Invalid email or password")
            
            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                raise ValueError("Invalid email or password")
            
            # Check if user is active
            if user.status != "active":
                raise ValueError("User account is not active")
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Create access token
            access_token = create_access_token(
                data={"sub": user.id, "email": user.email, "username": user.username}
            )
            
            # Create refresh token
            refresh_token = create_refresh_token(
                data={"sub": user.id, "email": user.email}
            )
            
            # Create session
            session_token = generate_session_token()
            session_expires = datetime.utcnow() + timedelta(days=7)
            
            new_session = UserSessionDB(
                id=str(uuid.uuid4()),
                user_id=user.id,
                session_token=session_token,
                created_at=datetime.utcnow(),
                expires_at=session_expires,
                is_active=True,
                ip_address=ip_address or "",
                user_agent=user_agent or ""
            )
            
            db.add(new_session)
            db.commit()
            
            logger.info(f"User logged in successfully: {user.email}")
            
            return {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "session_token": session_token,
                "token_type": "bearer"
            }
            
        except ValueError as e:
            logger.warning(f"User login failed: {e}")
            raise
        except Exception as e:
            logger.error(f"User login error: {e}")
            raise
        finally:
            db.close()
    
    async def logout_user(self, session_token: str) -> bool:
        """Logout a user by invalidating their session."""
        try:
            db = self.get_db()
            
            # Find and deactivate session
            session = db.query(UserSessionDB).filter(
                UserSessionDB.session_token == session_token,
                UserSessionDB.is_active == True
            ).first()
            
            if session:
                session.is_active = False
                db.commit()
                logger.info(f"User session invalidated: {session.user_id}")
                return True
            else:
                logger.warning(f"Session not found or already inactive: {session_token}")
                return False
                
        except Exception as e:
            logger.error(f"Logout error: {e}")
            raise
        finally:
            db.close()
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an access token using a refresh token."""
        try:
            # Verify refresh token
            payload = verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                raise ValueError("Invalid refresh token")
            
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token payload")
            
            db = self.get_db()
            user = db.query(UserDB).filter(UserDB.id == user_id).first()
            
            if not user or user.status != "active":
                raise ValueError("User not found or inactive")
            
            # Create new access token
            access_token = create_access_token(
                data={"sub": user.id, "email": user.email, "username": user.username}
            )
            
            logger.info(f"Token refreshed for user: {user.email}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except ValueError as e:
            logger.warning(f"Token refresh failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise
        finally:
            db.close()
    
    async def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get current user from token."""
        try:
            payload = verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            db = self.get_db()
            user = db.query(UserDB).filter(UserDB.id == user_id).first()
            
            if not user or user.status != "active":
                return None
            
            # Convert to dict and sanitize
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login,
                "preferences": user.preferences,
                "metadata": user.user_metadata
            }
            
            return sanitize_user_data(user_dict)
            
        except Exception as e:
            logger.error(f"Get current user error: {e}")
            return None
        finally:
            db.close()
    
    async def validate_session(self, session_token: str) -> bool:
        """Validate if a session token is active."""
        try:
            db = self.get_db()
            
            session = db.query(UserSessionDB).filter(
                UserSessionDB.session_token == session_token,
                UserSessionDB.is_active == True,
                UserSessionDB.expires_at > datetime.utcnow()
            ).first()
            
            return session is not None
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False
        finally:
            db.close()
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user."""
        try:
            db = self.get_db()
            
            sessions = db.query(UserSessionDB).filter(
                UserSessionDB.user_id == user_id,
                UserSessionDB.is_active == True
            ).all()
            
            return [
                {
                    "id": session.id,
                    "created_at": session.created_at,
                    "expires_at": session.expires_at,
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent
                }
                for session in sessions
            ]
            
        except Exception as e:
            logger.error(f"Get user sessions error: {e}")
            return []
        finally:
            db.close()
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions."""
        try:
            db = self.get_db()
            
            expired_sessions = db.query(UserSessionDB).filter(
                UserSessionDB.expires_at < datetime.utcnow(),
                UserSessionDB.is_active == True
            ).all()
            
            count = len(expired_sessions)
            for session in expired_sessions:
                session.is_active = False
            
            db.commit()
            
            if count > 0:
                logger.info(f"Cleaned up {count} expired sessions")
            
            return count
            
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
            return 0
        finally:
            db.close() 