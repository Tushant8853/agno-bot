"""
WebSocket API for real-time chat functionality.
"""

import json
import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
import structlog

from app.models.chat import (
    ChatMessage,
    MessageRole,
    MessageStatus,
    TypingIndicator
)
from app.models.memory import MemoryContext
from app.services.memory_service import MemoryService
from app.services.gemini_service import GeminiService
from app.services.agno_service import AgnoService
from app.middleware.error_logging import (
    log_websocket_error,
    log_api_error
)

logger = structlog.get_logger()

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, str] = {}  # session_id -> connection_id
        
    async def connect(self, websocket: WebSocket, session_id: str) -> str:
        """Connect a new WebSocket client."""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        self.session_connections[session_id] = connection_id
        
        logger.info(f"WebSocket connected: {connection_id} for session: {session_id}")
        return connection_id
    
    def disconnect(self, connection_id: str, session_id: str):
        """Disconnect a WebSocket client."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if session_id in self.session_connections:
            del self.session_connections[session_id]
        
        logger.info(f"WebSocket disconnected: {connection_id} for session: {session_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
    
    async def send_to_session(self, message: Dict[str, Any], session_id: str):
        """Send a message to a specific session."""
        connection_id = self.session_connections.get(session_id)
        if connection_id:
            await self.send_personal_message(message, connection_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connections."""
        for connection_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, connection_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: Optional[str] = None
):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
        user_id: User identifier (optional)
    """
    connection_id = None
    
    try:
        # Connect to WebSocket
        connection_id = await manager.connect(websocket, session_id)
        
        # Send connection confirmation
        await manager.send_personal_message({
            "type": "connection_established",
            "session_id": session_id,
            "connection_id": connection_id,
            "timestamp": str(uuid.uuid4())
        }, connection_id)
        
        # Handle incoming messages
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            await process_websocket_message(
                message_data,
                session_id,
                user_id,
                connection_id
            )
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(
            f"❌ WebSocket error: {e}",
            session_id=session_id,
            connection_id=connection_id,
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
    finally:
        if connection_id:
            manager.disconnect(connection_id, session_id)


async def process_websocket_message(
    message_data: Dict[str, Any],
    session_id: str,
    user_id: Optional[str],
    connection_id: str
):
    """
    Process incoming WebSocket message.
    
    Args:
        message_data: Message data from client
        session_id: Session identifier
        user_id: User identifier
        connection_id: Connection identifier
    """
    try:
        message_type = message_data.get("type")
        
        if message_type == "chat_message":
            await handle_chat_message(message_data, session_id, user_id, connection_id)
        elif message_type == "typing_start":
            await handle_typing_start(message_data, session_id, user_id, connection_id)
        elif message_type == "typing_stop":
            await handle_typing_stop(message_data, session_id, user_id, connection_id)
        elif message_type == "memory_query":
            await handle_memory_query(message_data, session_id, user_id, connection_id)
        else:
            logger.warning(f"Unknown message type: {message_type}")
            
    except Exception as e:
        logger.error(
            f"❌ Error processing WebSocket message: {e}",
            session_id=session_id,
            connection_id=connection_id,
            user_id=user_id,
            message_type=message_data.get("type"),
            error_type=type(e).__name__,
            error_message=str(e)
        )
        await manager.send_personal_message({
            "type": "error",
            "message": "Error processing message",
            "timestamp": str(uuid.uuid4())
        }, connection_id)


async def handle_chat_message(
    message_data: Dict[str, Any],
    session_id: str,
    user_id: Optional[str],
    connection_id: str
):
    """Handle chat message from WebSocket."""
    try:
        # Extract message content
        content = message_data.get("message", "")
        if not content:
            return
        
        # Create user message
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=content,
            metadata=message_data.get("metadata")
        )
        
        # Send typing indicator
        await manager.send_personal_message({
            "type": "typing_indicator",
            "session_id": session_id,
            "is_typing": True,
            "timestamp": str(uuid.uuid4())
        }, connection_id)
        
        # TODO: Get services from dependency injection
        # For now, create mock services
        memory_service = MemoryService()
        gemini_service = GeminiService()
        agno_service = AgnoService()
        
        # Get memory context
        memory_context = await memory_service.get_memory_context(
            session_id=session_id,
            user_id=user_id,
            query=content
        )
        
        # Generate AI response
        ai_response = await gemini_service.generate_response(
            message=content,
            memory_context=memory_context,
            conversation_history=None,
            system_prompt=None
        )
        
        # Create assistant message
        assistant_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=ai_response["response"],
            metadata=ai_response["metadata"]
        )
        
        # Send assistant response
        await manager.send_personal_message({
            "type": "chat_message",
            "message": ai_response["response"],
            "session_id": session_id,
            "message_id": str(uuid.uuid4()),
            "role": "assistant",
            "timestamp": str(uuid.uuid4()),
            "metadata": {
                "memory_context": {
                    "facts": [fact.content for fact in memory_context.facts] if memory_context else [],
                    "relationships": [
                        f"{rel.source_entity} {rel.relationship_type} {rel.target_entity}"
                        for rel in memory_context.relationships
                    ] if memory_context else [],
                    "summary": memory_context.context_summary if memory_context else None
                },
                "gemini_metadata": ai_response["metadata"]
            } if memory_context else None
        }, connection_id)
        
        # Stop typing indicator
        await manager.send_personal_message({
            "type": "typing_indicator",
            "session_id": session_id,
            "is_typing": False,
            "timestamp": str(uuid.uuid4())
        }, connection_id)
        
        # Process message through memory (background)
        # TODO: Implement background task processing
        
        logger.info(
            "Processed WebSocket chat message",
            session_id=session_id,
            message_length=len(content),
            response_length=len(ai_response["response"])
        )
        
    except Exception as e:
        logger.error(f"❌ Error handling chat message: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": "Error processing chat message",
            "timestamp": str(uuid.uuid4())
        }, connection_id)


async def handle_typing_start(
    message_data: Dict[str, Any],
    session_id: str,
    user_id: Optional[str],
    connection_id: str
):
    """Handle typing start indicator."""
    try:
        typing_indicator = TypingIndicator(
            session_id=session_id,
            is_typing=True,
            user_id=user_id
        )
        
        await manager.send_personal_message({
            "type": "typing_indicator",
            "session_id": session_id,
            "is_typing": True,
            "user_id": user_id,
            "timestamp": str(uuid.uuid4())
        }, connection_id)
        
    except Exception as e:
        logger.error(f"❌ Error handling typing start: {e}")


async def handle_typing_stop(
    message_data: Dict[str, Any],
    session_id: str,
    user_id: Optional[str],
    connection_id: str
):
    """Handle typing stop indicator."""
    try:
        await manager.send_personal_message({
            "type": "typing_indicator",
            "session_id": session_id,
            "is_typing": False,
            "user_id": user_id,
            "timestamp": str(uuid.uuid4())
        }, connection_id)
        
    except Exception as e:
        logger.error(f"❌ Error handling typing stop: {e}")


async def handle_memory_query(
    message_data: Dict[str, Any],
    session_id: str,
    user_id: Optional[str],
    connection_id: str
):
    """Handle memory query from WebSocket."""
    try:
        query = message_data.get("query", "")
        if not query:
            return
        
        # TODO: Get memory service from dependency injection
        memory_service = MemoryService()
        
        # Search memory
        search_result = await memory_service.search_memory(
            query=query,
            session_id=session_id,
            user_id=user_id,
            limit=10
        )
        
        # Send search results
        await manager.send_personal_message({
            "type": "memory_query_result",
            "query": query,
            "results": [
                {
                    "content": result.content,
                    "source": result.source.value,
                    "confidence": result.confidence,
                    "metadata": result.metadata
                }
                for result in search_result.results
            ],
            "total_count": search_result.total_count,
            "search_time_ms": search_result.search_time_ms,
            "timestamp": str(uuid.uuid4())
        }, connection_id)
        
        logger.info(
            "Processed WebSocket memory query",
            session_id=session_id,
            query=query,
            results_count=len(search_result.results)
        )
        
    except Exception as e:
        logger.error(f"❌ Error handling memory query: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": "Error processing memory query",
            "timestamp": str(uuid.uuid4())
        }, connection_id)


@router.get("/connections")
async def get_connection_stats() -> Dict[str, Any]:
    """Get WebSocket connection statistics."""
    return {
        "active_connections": len(manager.active_connections),
        "session_connections": len(manager.session_connections),
        "connection_ids": list(manager.active_connections.keys()),
        "session_ids": list(manager.session_connections.keys())
    }


@router.get("/health")
async def websocket_health() -> Dict[str, str]:
    """Health check for WebSocket API."""
    return {"status": "healthy", "service": "websocket"} 