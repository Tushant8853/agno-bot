"""
Main FastAPI application for the Agno chatbot.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.config import settings, validate_environment
from app.utils.logger import setup_logging
from app.api import chat, memory, websocket, auth
from app.services.memory_service import MemoryService
from app.services.gemini_service import GeminiService
from app.services.agno_service import AgnoService
from app.services.auth_service import AuthService
from app.deps import get_memory_service, get_gemini_service, get_agno_service, get_auth_service


# Setup logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting Agno Bot application")
    
    # Validate environment
    if not validate_environment():
        raise RuntimeError("Environment validation failed")
    
    # Initialize services
    try:
        app.state.memory_service = MemoryService()
        app.state.gemini_service = GeminiService()
        app.state.agno_service = AgnoService()
        app.state.auth_service = AuthService()
        
        # Initialize services
        await app.state.memory_service.initialize()
        await app.state.gemini_service.initialize()
        await app.state.agno_service.initialize()
        
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Agno Bot application")
    try:
        await app.state.memory_service.cleanup()
        await app.state.gemini_service.cleanup()
        await app.state.agno_service.cleanup()
        logger.info("✅ All services cleaned up successfully")
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Advanced chatbot with hybrid memory systems (Zep + Mem0) and Gemini AI",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with comprehensive error logging."""
    from app.middleware.error_logging import log_api_error
    
    # Log the error with full details
    error_id = log_api_error(
        error=exc,
        request=request,
        endpoint=request.url.path,
        operation="global_exception_handler",
        context={
            "method": request.method,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    # Return error response with error ID for tracking
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": error_id,
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "services": {
            "memory": "initialized",
            "gemini": "initialized", 
            "agno": "initialized",
            "auth": "initialized"
        }
    }


# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with application information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "description": "Advanced chatbot with hybrid memory systems",
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["websocket"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 