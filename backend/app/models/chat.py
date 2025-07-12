"""
Chat-related Pydantic models.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    """Message status enumeration."""
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ERROR = "error"


class ChatMessage(BaseModel):
    """Chat message model."""
    id: Optional[str] = None
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: MessageStatus = MessageStatus.SENT
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    memory_context: Optional[bool] = True
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Hello, how are you?",
                "session_id": "session_123",
                "user_id": "user_456",
                "context": {"topic": "greeting"},
                "memory_context": True
            }
        }


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    session_id: str
    message_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    memory_context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "message": "Hello! I'm doing well, thank you for asking. How can I help you today?",
                "session_id": "session_123",
                "message_id": "msg_789",
                "timestamp": "2024-01-01T12:00:00Z",
                "memory_context": {
                    "facts": ["User prefers formal greetings"],
                    "relationships": ["User is a returning customer"]
                },
                "metadata": {
                    "model": "gemini-1.5-pro",
                    "tokens_used": 45
                }
            }
        }


class ChatSession(BaseModel):
    """Chat session model."""
    id: str
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[ChatMessage] = []
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatHistory(BaseModel):
    """Chat history model."""
    session_id: str
    messages: List[ChatMessage]
    total_messages: int
    created_at: datetime
    last_activity: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TypingIndicator(BaseModel):
    """Typing indicator model."""
    session_id: str
    is_typing: bool
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 