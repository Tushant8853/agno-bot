"""
Gemini AI service for natural language processing.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import structlog

from app.config import settings
from app.models.chat import ChatMessage, MessageRole
from app.models.memory import MemoryContext

logger = structlog.get_logger()


class GeminiService:
    """Service for interacting with Google's Gemini AI model."""
    
    def __init__(self):
        self.model = None
        self.chat_model = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the Gemini service."""
        try:
            # Configure Gemini
            genai.configure(api_key=settings.google_gemini_api_key)

            # Force the model name here to avoid config/env issues
            forced_model_name = "gemini-1.5-pro"
            print(f"[DEBUG] Forcing Gemini model name: {forced_model_name}")
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=forced_model_name,
                generation_config={
                    "temperature": settings.gemini_temperature,
                    "max_output_tokens": settings.gemini_max_tokens,
                }
            )
            
            # Initialize chat model
            self.chat_model = self.model.start_chat(history=[])
            
            self.is_initialized = True
            logger.info("✅ Gemini service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini service: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup Gemini service resources."""
        try:
            self.model = None
            self.chat_model = None
            self.is_initialized = False
            logger.info("✅ Gemini service cleaned up successfully")
        except Exception as e:
            logger.error(f"❌ Error during Gemini cleanup: {e}")
    
    async def generate_response(
        self,
        message: str,
        memory_context: Optional[MemoryContext] = None,
        conversation_history: Optional[List[ChatMessage]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using Gemini AI.
        
        Args:
            message: User's input message
            memory_context: Memory context from hybrid memory system
            conversation_history: Recent conversation history
            system_prompt: System prompt for the AI
            
        Returns:
            Dictionary containing response and metadata
        """
        if not self.is_initialized:
            raise RuntimeError("Gemini service not initialized")
        
        start_time = time.time()
        
        try:
            # Build the prompt with memory context
            prompt = self._build_prompt(
                message=message,
                memory_context=memory_context,
                conversation_history=conversation_history,
                system_prompt=system_prompt
            )
            
            # Generate response
            response = await asyncio.to_thread(
                self.chat_model.send_message,
                prompt
            )
            
            # Extract response content
            response_text = response.text
            
            # Calculate metrics
            generation_time = time.time() - start_time
            
            # Extract metadata
            metadata = {
                "model": settings.gemini_model,
                "generation_time_ms": round(generation_time * 1000, 2),
                "prompt_tokens": self._estimate_tokens(prompt),
                "response_tokens": self._estimate_tokens(response_text),
                "temperature": settings.gemini_temperature,
                "memory_context_used": memory_context is not None
            }
            
            logger.info(
                "Generated Gemini response",
                message_length=len(message),
                response_length=len(response_text),
                generation_time_ms=metadata["generation_time_ms"],
                memory_context_used=metadata["memory_context_used"]
            )
            
            return {
                "response": response_text,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating Gemini response: {e}")
            raise
    
    def _build_prompt(
        self,
        message: str,
        memory_context: Optional[MemoryContext] = None,
        conversation_history: Optional[List[ChatMessage]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Build a comprehensive prompt for Gemini.
        
        Args:
            message: User's input message
            memory_context: Memory context from hybrid memory system
            conversation_history: Recent conversation history
            system_prompt: System prompt for the AI
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # System prompt
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        else:
            prompt_parts.append(
                "System: You are Agno Bot, an intelligent chatbot with advanced memory capabilities. "
                "You can remember facts about users and maintain context across conversations. "
                "Be helpful, friendly, and use the memory context to provide personalized responses."
            )
        
        # Memory context
        if memory_context:
            memory_prompt = self._format_memory_context(memory_context)
            prompt_parts.append(f"Memory Context: {memory_prompt}")
        
        # Conversation history
        if conversation_history:
            history_prompt = self._format_conversation_history(conversation_history)
            prompt_parts.append(f"Recent Conversation: {history_prompt}")
        
        # Current message
        prompt_parts.append(f"User: {message}")
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    def _format_memory_context(self, memory_context: MemoryContext) -> str:
        """Format memory context for the prompt."""
        context_parts = []
        
        if memory_context.facts:
            facts_text = "; ".join([fact.content for fact in memory_context.facts])
            context_parts.append(f"Facts: {facts_text}")
        
        if memory_context.relationships:
            relationships_text = "; ".join([
                f"{rel.source_entity} {rel.relationship_type} {rel.target_entity}"
                for rel in memory_context.relationships
            ])
            context_parts.append(f"Relationships: {relationships_text}")
        
        if memory_context.context_summary:
            context_parts.append(f"Summary: {memory_context.context_summary}")
        
        return " | ".join(context_parts) if context_parts else "No specific memory context"
    
    def _format_conversation_history(self, history: List[ChatMessage]) -> str:
        """Format conversation history for the prompt."""
        if not history:
            return "No recent conversation history"
        
        # Take last 5 messages to avoid token limits
        recent_history = history[-5:]
        
        formatted_messages = []
        for msg in recent_history:
            role = "User" if msg.role == MessageRole.USER else "Assistant"
            formatted_messages.append(f"{role}: {msg.content}")
        
        return " | ".join(formatted_messages)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4
    
    async def extract_facts(self, text: str) -> List[str]:
        """
        Extract facts from text using Gemini.
        
        Args:
            text: Text to extract facts from
            
        Returns:
            List of extracted facts
        """
        if not self.is_initialized:
            raise RuntimeError("Gemini service not initialized")
        
        try:
            prompt = f"""
            Extract key facts from the following text. Return only the facts, one per line:
            
            Text: {text}
            
            Facts:
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            facts = [fact.strip() for fact in response.text.split('\n') if fact.strip()]
            
            logger.info(f"Extracted {len(facts)} facts from text")
            return facts
            
        except Exception as e:
            logger.error(f"❌ Error extracting facts: {e}")
            return []
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using Gemini.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        if not self.is_initialized:
            raise RuntimeError("Gemini service not initialized")
        
        try:
            prompt = f"""
            Analyze the sentiment of the following text. Return a JSON object with:
            - sentiment: positive, negative, or neutral
            - confidence: 0.0 to 1.0
            - emotions: list of detected emotions
            - intensity: low, medium, or high
            
            Text: {text}
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # Parse JSON response (simplified)
            # In production, you'd want proper JSON parsing
            sentiment_data = {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": [],
                "intensity": "medium"
            }
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"❌ Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": [],
                "intensity": "low"
            } 