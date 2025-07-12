"""
Logging configuration for the Agno chatbot application.
"""

import logging
import sys
from typing import Optional
import structlog
from structlog.stdlib import LoggerFactory

from app.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None
):
    """
    Setup structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json, console)
    """
    # Use settings if not provided
    log_level = log_level or settings.log_level
    log_format = log_format or settings.log_format
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if log_format == "json" else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Create logger instance
    logger = structlog.get_logger()
    logger.info(
        "Logging configured",
        log_level=log_level,
        log_format=log_format
    )
    
    return logger


def get_logger(name: str = None):
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def log_request(request_id: str, method: str, path: str, status_code: int, duration_ms: float):
    """
    Log HTTP request information.
    
    Args:
        request_id: Unique request identifier
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
    """
    logger = get_logger("http")
    logger.info(
        "HTTP request",
        request_id=request_id,
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms
    )


def log_error(error: Exception, context: dict = None):
    """
    Log error information.
    
    Args:
        error: Exception that occurred
        context: Additional context information
    """
    logger = get_logger("error")
    logger.error(
        "Application error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    )


def log_memory_operation(operation: str, session_id: str, user_id: str = None, **kwargs):
    """
    Log memory system operations.
    
    Args:
        operation: Memory operation type
        session_id: Session identifier
        user_id: User identifier
        **kwargs: Additional operation parameters
    """
    logger = get_logger("memory")
    logger.info(
        "Memory operation",
        operation=operation,
        session_id=session_id,
        user_id=user_id,
        **kwargs
    )


def log_chat_message(session_id: str, message_type: str, message_length: int, **kwargs):
    """
    Log chat message information.
    
    Args:
        session_id: Session identifier
        message_type: Type of message (user, assistant)
        message_length: Length of message
        **kwargs: Additional message parameters
    """
    logger = get_logger("chat")
    logger.info(
        "Chat message",
        session_id=session_id,
        message_type=message_type,
        message_length=message_length,
        **kwargs
    ) 