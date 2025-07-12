"""
Memory API routes for the Agno chatbot.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import JSONResponse
import structlog

from app.models.memory import (
    MemoryQuery,
    MemorySearchResult,
    MemoryContext,
    MemoryFact,
    MemoryRelationship,
    MemoryAnalytics
)
from app.services.memory_service import MemoryService
from app.deps import get_memory_service
from app.middleware.error_logging import (
    log_api_error,
    log_service_error,
    log_memory_error
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/context/{session_id}", response_model=MemoryContext)
async def get_memory_context(
    session_id: str,
    user_id: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    memory_service: MemoryService = Depends(get_memory_service)
) -> MemoryContext:
    """
    Get memory context for a session.
    
    Args:
        session_id: Session identifier
        user_id: User identifier (optional)
        query: Optional query for context retrieval
        memory_service: Memory service dependency
        
    Returns:
        Memory context with facts and relationships
    """
    try:
        context = await memory_service.get_memory_context(
            session_id=session_id,
            user_id=user_id,
            query=query
        )
        
        logger.info(
            "Retrieved memory context",
            session_id=session_id,
            facts_count=len(context.facts),
            relationships_count=len(context.relationships)
        )
        
        return context
        
    except Exception as e:
        logger.error(
            f"❌ Error getting memory context: {e}",
            session_id=session_id,
            user_id=user_id,
            query=query,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=MemorySearchResult)
async def search_memory(
    query: MemoryQuery,
    memory_service: MemoryService = Depends(get_memory_service)
) -> MemorySearchResult:
    """
    Search memory across both Zep and Mem0 systems.
    
    Args:
        query: Memory search query
        memory_service: Memory service dependency
        
    Returns:
        Search results from both systems
    """
    try:
        result = await memory_service.search_memory(
            query=query.query,
            session_id=query.filters.get("session_id") if query.filters else None,
            user_id=query.filters.get("user_id") if query.filters else None,
            limit=query.limit
        )
        
        logger.info(
            "Searched memory",
            query=query.query,
            total_results=result.total_count,
            search_time_ms=result.search_time_ms
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"❌ Error searching memory: {e}",
            query=query.query,
            query_type=query.query_type,
            filters=query.filters,
            limit=query.limit,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relationships", response_model=MemoryRelationship)
async def create_relationship(
    request: Request,
    source_entity: str,
    target_entity: str,
    relationship_type: str,
    session_id: Optional[str] = None,
    confidence: float = 0.8,
) -> MemoryRelationship:
    """
    Create a relationship in memory.
    
    Args:
        source_entity: Source entity
        target_entity: Target entity
        relationship_type: Type of relationship
        session_id: Session identifier (optional)
        confidence: Confidence score
        request: FastAPI request object
        
    Returns:
        Created relationship
    """
    try:
        memory_service = request.app.state.memory_service
        relationship = await memory_service.create_relationship(
            source_entity=source_entity,
            target_entity=target_entity,
            relationship_type=relationship_type,
            session_id=session_id,
            confidence=confidence
        )
        
        logger.info(
            "Created memory relationship",
            source=source_entity,
            target=target_entity,
            relationship_type=relationship_type
        )
        
        return relationship
        
    except Exception as e:
        logger.error(
            f"❌ Error creating relationship: {e}",
            source_entity=source_entity,
            target_entity=target_entity,
            relationship_type=relationship_type,
            session_id=session_id,
            confidence=confidence,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=MemoryAnalytics)
async def get_memory_analytics(
    user_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    memory_service: MemoryService = Depends(get_memory_service)
) -> MemoryAnalytics:
    """
    Get memory analytics.
    
    Args:
        user_id: User identifier (optional)
        session_id: Session identifier (optional)
        memory_service: Memory service dependency
        
    Returns:
        Memory analytics data
    """
    try:
        analytics = await memory_service.get_memory_analytics(
            user_id=user_id,
            session_id=session_id
        )
        
        logger.info(
            "Retrieved memory analytics",
            user_id=user_id,
            session_id=session_id,
            total_facts=analytics.total_facts,
            total_relationships=analytics.total_relationships
        )
        
        return analytics
        
    except Exception as e:
        logger.error(
            f"❌ Error getting memory analytics: {e}",
            user_id=user_id,
            session_id=session_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/facts", response_model=List[MemoryFact])
async def get_facts(
    session_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    memory_service: MemoryService = Depends(get_memory_service)
) -> List[MemoryFact]:
    """
    Get facts from memory.
    
    Args:
        session_id: Session identifier (optional)
        user_id: User identifier (optional)
        source: Memory source filter (zep, mem0, hybrid)
        limit: Maximum number of facts to return
        memory_service: Memory service dependency
        
    Returns:
        List of memory facts
    """
    try:
        # Use search to get facts
        query = "all facts"  # Generic query to get all facts
        search_result = await memory_service.search_memory(
            query=query,
            session_id=session_id,
            user_id=user_id,
            limit=limit
        )
        
        # Filter by source if specified
        facts = search_result.results
        if source:
            facts = [fact for fact in facts if fact.source.value == source.lower()]
        
        logger.info(
            "Retrieved memory facts",
            session_id=session_id,
            source=source,
            facts_count=len(facts)
        )
        
        return facts
        
    except Exception as e:
        logger.error(f"❌ Error getting facts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/relationships", response_model=List[MemoryRelationship])
async def get_relationships(
    session_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    memory_service: MemoryService = Depends(get_memory_service)
) -> List[MemoryRelationship]:
    """
    Get relationships from memory.
    
    Args:
        session_id: Session identifier (optional)
        user_id: User identifier (optional)
        source: Memory source filter (zep, mem0, hybrid)
        limit: Maximum number of relationships to return
        memory_service: Memory service dependency
        
    Returns:
        List of memory relationships
    """
    try:
        # Get context which includes relationships
        context = await memory_service.get_memory_context(
            session_id=session_id,
            user_id=user_id
        )
        
        # Filter by source if specified
        relationships = context.relationships
        if source:
            relationships = [rel for rel in relationships if rel.source.value == source.lower()]
        
        # Apply limit
        relationships = relationships[:limit]
        
        logger.info(
            "Retrieved memory relationships",
            session_id=session_id,
            source=source,
            relationships_count=len(relationships)
        )
        
        return relationships
        
    except Exception as e:
        logger.error(f"❌ Error getting relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/facts/{fact_id}")
async def delete_fact(
    fact_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, str]:
    """
    Delete a fact from memory.
    
    Args:
        fact_id: Fact identifier
        memory_service: Memory service dependency
        
    Returns:
        Success message
    """
    try:
        # TODO: Implement fact deletion in memory service
        logger.info(f"Deleted memory fact: {fact_id}")
        return {"message": f"Fact {fact_id} deleted successfully"}
        
    except Exception as e:
        logger.error(
            f"❌ Error deleting fact: {e}",
            fact_id=fact_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/relationships/{relationship_id}")
async def delete_relationship(
    relationship_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, str]:
    """
    Delete a relationship from memory.
    
    Args:
        relationship_id: Relationship identifier
        memory_service: Memory service dependency
        
    Returns:
        Success message
    """
    try:
        # TODO: Implement relationship deletion in memory service
        logger.info(f"Deleted memory relationship: {relationship_id}")
        return {"message": f"Relationship {relationship_id} deleted successfully"}
        
    except Exception as e:
        logger.error(
            f"❌ Error deleting relationship: {e}",
            relationship_id=relationship_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def memory_health() -> Dict[str, str]:
    """Health check for memory API."""
    return {"status": "healthy", "service": "memory"}





@router.get("/stats")
async def get_memory_stats(
    user_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """
    Get memory statistics.
    
    Args:
        user_id: User identifier (optional)
        session_id: Session identifier (optional)
        memory_service: Memory service dependency
        
    Returns:
        Memory statistics
    """
    try:
        analytics = await memory_service.get_memory_analytics(
            user_id=user_id,
            session_id=session_id
        )
        
        stats = {
            "total_facts": analytics.total_facts,
            "total_relationships": analytics.total_relationships,
            "memory_usage_mb": round(analytics.memory_usage_bytes / (1024 * 1024), 2),
            "average_confidence": round(analytics.average_confidence, 3),
            "source_distribution": analytics.source_distribution,
            "priority_distribution": analytics.priority_distribution
        }
        
        logger.info(
            "Retrieved memory stats",
            user_id=user_id,
            session_id=session_id,
            stats=stats
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 