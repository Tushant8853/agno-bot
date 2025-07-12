"""
Memory-related Pydantic models.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Memory type enumeration."""
    FACT = "fact"
    RELATIONSHIP = "relationship"
    CONTEXT = "context"
    SESSION = "session"


class MemorySource(str, Enum):
    """Memory source enumeration."""
    ZEP = "zep"
    MEM0 = "mem0"
    HYBRID = "hybrid"


class MemoryPriority(str, Enum):
    """Memory priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryFact(BaseModel):
    """Memory fact model."""
    id: Optional[str] = None
    content: str
    source: MemorySource
    priority: MemoryPriority = MemoryPriority.MEDIUM
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "content": "User prefers formal greetings",
                "source": "mem0",
                "priority": "medium",
                "confidence": 0.9,
                "tags": ["preference", "greeting"]
            }
        }


class MemoryRelationship(BaseModel):
    """Memory relationship model."""
    id: Optional[str] = None
    source_entity: str
    target_entity: str
    relationship_type: str
    source: MemorySource
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "source_entity": "user_123",
                "target_entity": "topic_ai",
                "relationship_type": "interested_in",
                "source": "zep",
                "confidence": 0.85
            }
        }


class MemoryContext(BaseModel):
    """Memory context model."""
    session_id: str
    user_id: Optional[str] = None
    facts: List[MemoryFact] = []
    relationships: List[MemoryRelationship] = []
    context_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemoryQuery(BaseModel):
    """Memory query model."""
    query: str
    query_type: str = "semantic"  # semantic, fact, relationship
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(default=10, ge=1, le=100)
    include_metadata: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "query": "user preferences",
                "query_type": "semantic",
                "filters": {"source": "mem0"},
                "limit": 5
            }
        }


class MemorySearchResult(BaseModel):
    """Memory search result model."""
    query: str
    results: List[Union[MemoryFact, MemoryRelationship]]
    total_count: int
    search_time_ms: float
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "query": "user preferences",
                "total_count": 3,
                "search_time_ms": 45.2
            }
        }


class MemoryConsolidation(BaseModel):
    """Memory consolidation model."""
    source_facts: List[MemoryFact]
    consolidated_fact: MemoryFact
    consolidation_reason: str
    confidence_boost: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemoryAnalytics(BaseModel):
    """Memory analytics model."""
    total_facts: int
    total_relationships: int
    memory_usage_bytes: int
    average_confidence: float
    source_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


 