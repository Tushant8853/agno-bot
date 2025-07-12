"""
Chat API routes for the Agno chatbot.
"""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import structlog

from app.models.chat import (
    ChatRequest, 
    ChatResponse, 
    ChatSession, 
    ChatHistory,
    ChatMessage,
    MessageRole,
    MessageStatus
)
from app.models.memory import MemoryContext
from app.services.memory_service import MemoryService
from app.services.gemini_service import GeminiService
from app.services.agno_service import AgnoService
from app.deps import get_memory_service, get_gemini_service, get_agno_service
from app.middleware.error_logging import (
    log_api_error,
    log_service_error,
    log_validation_error
)

logger = structlog.get_logger()

router = APIRouter()


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    background_tasks: BackgroundTasks,
    memory_service: MemoryService = Depends(get_memory_service),
    gemini_service: GeminiService = Depends(get_gemini_service),
    agno_service: AgnoService = Depends(get_agno_service)
) -> ChatResponse:
    """
    Send a message to the chatbot and get a response.
    
    Args:
        request: Chat request with message and session info
        background_tasks: FastAPI background tasks
        memory_service: Memory service dependency
        gemini_service: Gemini service dependency
        agno_service: Agno service dependency
        
    Returns:
        Chat response with AI-generated message
    """
    try:
        # Generate session ID if not provided
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        # Create user message
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=chat_request.message,
            metadata=chat_request.context
        )
        
        # Process with Agno framework
        agno_result = await agno_service.process_conversation(
            session_id=session_id,
            user_message=chat_request.message,
            memory_context=None  # Will be populated after memory retrieval
        )
        
        # Get memory context if requested
        memory_context = None
        if chat_request.memory_context:
            memory_context = await memory_service.get_memory_context(
                session_id=session_id,
                user_id=chat_request.user_id,
                query=chat_request.message
            )
        
        # Generate AI response using Gemini
        ai_response = await gemini_service.generate_response(
            message=chat_request.message,
            memory_context=memory_context,
            conversation_history=None,  # TODO: Get from Agno session
            system_prompt=None
        )
        
        # Create assistant message
        assistant_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=ai_response["response"],
            metadata=ai_response["metadata"]
        )
        
        # Add messages to Agno session
        await agno_service.add_message_to_session(session_id, user_message)
        await agno_service.add_message_to_session(session_id, assistant_message)
        
        # Process message through memory systems (background task)
        background_tasks.add_task(
            process_message_memory,
            memory_service,
            user_message,
            session_id,
            chat_request.user_id
        )
        
        # Create response
        response = ChatResponse(
            message=ai_response["response"],
            session_id=session_id,
            message_id=str(uuid.uuid4()),
            memory_context={
                "facts": [fact.content for fact in memory_context.facts] if memory_context else [],
                "relationships": [
                    f"{rel.source_entity} {rel.relationship_type} {rel.target_entity}"
                    for rel in memory_context.relationships
                ] if memory_context else [],
                "summary": memory_context.context_summary if memory_context else None
            } if memory_context else None,
            metadata={
                "agno_result": agno_result,
                "gemini_metadata": ai_response["metadata"]
            }
        )
        
        logger.info(
            "Generated chat response",
            session_id=session_id,
            message_length=len(chat_request.message),
            response_length=len(ai_response["response"]),
            memory_context_used=memory_context is not None
        )
        
        return response
        
    except Exception as e:
        # Log detailed error information
        logger.error(
            f"❌ Error in send_message: {e}",
            session_id=session_id,
            user_id=chat_request.user_id,
            message_length=len(chat_request.message),
            memory_context_requested=chat_request.memory_context,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions", response_model=ChatSession)
async def create_session(
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    agno_service: AgnoService = Depends(get_agno_service)
) -> ChatSession:
    """
    Create a new chat session.
    
    Args:
        user_id: User identifier
        metadata: Session metadata
        agno_service: Agno service dependency
        
    Returns:
        Created chat session
    """
    try:
        session = await agno_service.create_session(
            user_id=user_id,
            metadata=metadata or {}
        )
        
        logger.info(f"Created new chat session: {session.id}")
        return session
        
    except Exception as e:
        logger.error(
            f"❌ Error creating session: {e}",
            user_id=user_id,
            metadata=metadata,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
    session_id: str,
    agno_service: AgnoService = Depends(get_agno_service)
) -> ChatSession:
    """
    Get a chat session by ID.
    
    Args:
        session_id: Session identifier
        agno_service: Agno service dependency
        
    Returns:
        Chat session
    """
    try:
        session = await agno_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Error getting session: {e}",
            session_id=session_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history", response_model=ChatHistory)
async def get_session_history(
    session_id: str,
    limit: Optional[int] = 50,
    agno_service: AgnoService = Depends(get_agno_service)
) -> ChatHistory:
    """
    Get message history for a session.
    
    Args:
        session_id: Session identifier
        limit: Maximum number of messages to return
        agno_service: Agno service dependency
        
    Returns:
        Chat history
    """
    try:
        session = await agno_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = await agno_service.get_session_history(session_id, limit)
        
        history = ChatHistory(
            session_id=session_id,
            messages=messages,
            total_messages=len(messages),
            created_at=session.created_at,
            last_activity=session.updated_at
        )
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Error getting session history: {e}",
            session_id=session_id,
            limit=limit,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def close_session(
    session_id: str,
    agno_service: AgnoService = Depends(get_agno_service)
) -> Dict[str, str]:
    """
    Close a chat session.
    
    Args:
        session_id: Session identifier
        agno_service: Agno service dependency
        
    Returns:
        Success message
    """
    try:
        success = await agno_service.close_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Closed chat session: {session_id}")
        return {"message": f"Session {session_id} closed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Error closing session: {e}",
            session_id=session_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/analytics")
async def get_session_analytics(
    session_id: str,
    agno_service: AgnoService = Depends(get_agno_service)
) -> Dict[str, Any]:
    """
    Get analytics for a chat session.
    
    Args:
        session_id: Session identifier
        agno_service: Agno service dependency
        
    Returns:
        Session analytics
    """
    try:
        analytics = await agno_service.get_session_analytics(session_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Error getting session analytics: {e}",
            session_id=session_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def chat_health() -> Dict[str, str]:
    """Health check for chat API."""
    return {"status": "healthy", "service": "chat"}


async def process_message_memory(
    memory_service: MemoryService,
    message: ChatMessage,
    session_id: str,
    user_id: Optional[str]
):
    """
    Process message through memory systems (background task).
    
    Args:
        memory_service: Memory service
        message: Chat message to process
        session_id: Session identifier
        user_id: User identifier
    """
    try:
        result = await memory_service.process_message(
            message=message,
            session_id=session_id,
            user_id=user_id
        )
        
        logger.info(
            "Processed message through memory systems",
            session_id=session_id,
            result=result
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing message memory: {e}") 