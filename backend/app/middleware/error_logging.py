"""
Error logging middleware for comprehensive error tracking.
"""

import time
import traceback
import uuid
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import structlog

from app.utils.logger import get_logger

logger = get_logger("error_middleware")


class ErrorLoggingMiddleware:
    """Middleware for comprehensive error logging."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Create request object
        request = Request(scope)
        
        # Log request start
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            content_length=request.headers.get("content-length")
        )
        
        try:
            # Process request
            await self.app(scope, receive, send)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful request
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                duration_ms=round(duration_ms, 2),
                status="success"
            )
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Get full traceback
            tb = traceback.format_exc()
            
            # Log detailed error information
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=tb,
                status="error"
            )
            
            # Re-raise the exception
            raise


def log_api_error(
    error: Exception,
    request: Request,
    endpoint: str,
    operation: str,
    context: Optional[Dict[str, Any]] = None
):
    """
    Log detailed API error information.
    
    Args:
        error: The exception that occurred
        request: FastAPI request object
        endpoint: API endpoint name
        operation: Operation being performed
        context: Additional context information
    """
    # Generate error ID
    error_id = str(uuid.uuid4())
    
    # Get request details
    request_details = {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }
    
    # Get error details
    error_details = {
        "error_id": error_id,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "error_module": error.__class__.__module__,
        "traceback": traceback.format_exc()
    }
    
    # Log comprehensive error information
    logger.error(
        "API Error",
        error_id=error_id,
        endpoint=endpoint,
        operation=operation,
        request_details=request_details,
        error_details=error_details,
        context=context or {},
        timestamp=time.time()
    )
    
    return error_id


async def log_validation_error(
    error: Exception,
    request: Request,
    endpoint: str,
    field_errors: Optional[Dict[str, Any]] = None
):
    """
    Log validation errors specifically.
    
    Args:
        error: Validation exception
        request: FastAPI request object
        endpoint: API endpoint name
        field_errors: Field-specific validation errors
    """
    error_id = str(uuid.uuid4())
    
    # Get request body safely
    request_body = None
    try:
        request_body = await request.body()
    except Exception:
        pass
    
    logger.error(
        "Validation Error",
        error_id=error_id,
        endpoint=endpoint,
        error_type="ValidationError",
        error_message=str(error),
        field_errors=field_errors or {},
        request_body=request_body,
        request_headers=dict(request.headers),
        timestamp=time.time()
    )
    
    return error_id


def log_service_error(
    error: Exception,
    service_name: str,
    operation: str,
    context: Optional[Dict[str, Any]] = None
):
    """
    Log service-specific errors.
    
    Args:
        error: Service exception
        service_name: Name of the service
        operation: Operation being performed
        context: Additional context
    """
    error_id = str(uuid.uuid4())
    
    logger.error(
        "Service Error",
        error_id=error_id,
        service_name=service_name,
        operation=operation,
        error_type=type(error).__name__,
        error_message=str(error),
        traceback=traceback.format_exc(),
        context=context or {},
        timestamp=time.time()
    )
    
    return error_id


def log_database_error(
    error: Exception,
    operation: str,
    table: Optional[str] = None,
    query: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
):
    """
    Log database-specific errors.
    
    Args:
        error: Database exception
        operation: Database operation
        table: Database table name
        query: SQL query (if applicable)
        context: Additional context
    """
    error_id = str(uuid.uuid4())
    
    logger.error(
        "Database Error",
        error_id=error_id,
        operation=operation,
        table=table,
        query=query,
        error_type=type(error).__name__,
        error_message=str(error),
        traceback=traceback.format_exc(),
        context=context or {},
        timestamp=time.time()
    )
    
    return error_id


def log_external_api_error(
    error: Exception,
    api_name: str,
    endpoint: str,
    request_data: Optional[Dict[str, Any]] = None,
    response_data: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None
):
    """
    Log external API errors.
    
    Args:
        error: External API exception
        api_name: Name of the external API
        endpoint: API endpoint
        request_data: Request data sent
        response_data: Response data received
        context: Additional context
    """
    error_id = str(uuid.uuid4())
    
    logger.error(
        "External API Error",
        error_id=error_id,
        api_name=api_name,
        endpoint=endpoint,
        error_type=type(error).__name__,
        error_message=str(error),
        request_data=request_data,
        response_data=response_data,
        traceback=traceback.format_exc(),
        context=context or {},
        timestamp=time.time()
    )
    
    return error_id


def log_websocket_error(
    error: Exception,
    session_id: str,
    operation: str,
    message_data: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None
):
    """
    Log WebSocket-specific errors.
    
    Args:
        error: WebSocket exception
        session_id: WebSocket session ID
        operation: Operation being performed
        message_data: Message data (if applicable)
        context: Additional context
    """
    error_id = str(uuid.uuid4())
    
    logger.error(
        "WebSocket Error",
        error_id=error_id,
        session_id=session_id,
        operation=operation,
        error_type=type(error).__name__,
        error_message=str(error),
        message_data=message_data,
        traceback=traceback.format_exc(),
        context=context or {},
        timestamp=time.time()
    )
    
    return error_id


def log_memory_error(
    error: Exception,
    operation: str,
    session_id: str,
    user_id: Optional[str] = None,
    memory_source: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
):
    """
    Log memory system errors.
    
    Args:
        error: Memory system exception
        operation: Memory operation
        session_id: Session ID
        user_id: User ID
        memory_source: Memory source (zep, mem0, hybrid)
        context: Additional context
    """
    error_id = str(uuid.uuid4())
    
    logger.error(
        "Memory System Error",
        error_id=error_id,
        operation=operation,
        session_id=session_id,
        user_id=user_id,
        memory_source=memory_source,
        error_type=type(error).__name__,
        error_message=str(error),
        traceback=traceback.format_exc(),
        context=context or {},
        timestamp=time.time()
    )
    
    return error_id


def log_authentication_error(
    error: Exception,
    request: Request,
    auth_method: str,
    user_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
):
    """
    Log authentication errors.
    
    Args:
        error: Authentication exception
        request: FastAPI request object
        auth_method: Authentication method used
        user_id: User ID (if available)
        context: Additional context
    """
    error_id = str(uuid.uuid4())
    
    logger.error(
        "Authentication Error",
        error_id=error_id,
        auth_method=auth_method,
        user_id=user_id,
        error_type=type(error).__name__,
        error_message=str(error),
        request_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        traceback=traceback.format_exc(),
        context=context or {},
        timestamp=time.time()
    )
    
    return error_id


def log_rate_limit_error(
    request: Request,
    limit_type: str,
    current_usage: int,
    limit: int,
    reset_time: Optional[int] = None
):
    """
    Log rate limiting errors.
    
    Args:
        request: FastAPI request object
        limit_type: Type of rate limit
        current_usage: Current usage count
        limit: Rate limit threshold
        reset_time: Time when limit resets
    """
    error_id = str(uuid.uuid4())
    
    logger.warning(
        "Rate Limit Exceeded",
        error_id=error_id,
        limit_type=limit_type,
        current_usage=current_usage,
        limit=limit,
        reset_time=reset_time,
        request_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        timestamp=time.time()
    )
    
    return error_id 