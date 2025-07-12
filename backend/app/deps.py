from fastapi import Request
from app.services.memory_service import MemoryService
from app.services.gemini_service import GeminiService
from app.services.agno_service import AgnoService
from app.services.auth_service import AuthService

def get_memory_service(request: Request) -> MemoryService:
    return request.app.state.memory_service

def get_gemini_service(request: Request) -> GeminiService:
    return request.app.state.gemini_service

def get_agno_service(request: Request) -> AgnoService:
    return request.app.state.agno_service

def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service 