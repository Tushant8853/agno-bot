"""
User-related Pydantic models.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(BaseModel):
    """User model."""
    id: Optional[str] = None
    username: str
    email: EmailStr
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "role": "user",
                "preferences": {
                    "theme": "dark",
                    "language": "en"
                }
            }
        }


class UserSession(BaseModel):
    """User session model."""
    id: str
    user_id: str
    session_token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_active: bool = True
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    """User creation model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserUpdate(BaseModel):
    """User update model."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe_updated",
                "preferences": {
                    "theme": "light",
                    "notifications": True
                }
            }
        }


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserProfile(BaseModel):
    """User profile model."""
    id: str
    username: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None
    session_count: int = 0
    total_messages: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserStats(BaseModel):
    """User statistics model."""
    user_id: str
    total_sessions: int
    total_messages: int
    average_session_duration: float  # in minutes
    favorite_topics: List[str] = []
    memory_facts_count: int
    memory_relationships_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 