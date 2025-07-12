"""
Zep memory service for temporal knowledge graph-based memory.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

from app.config import settings
from app.models.memory import (
    MemoryFact, 
    MemoryRelationship, 
    MemoryContext, 
    MemoryQuery,
    MemorySource,
    MemoryPriority
)
from app.models.chat import ChatMessage, MessageRole

logger = structlog.get_logger()


class ZepService:
    """Service for interacting with Zep memory system."""
    
    def __init__(self):
        self.client = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the Zep service."""
        try:
            # Import Zep client
            from zep_python import ZepClient
            
            # Initialize Zep client
            self.client = ZepClient(
                base_url=settings.zep_base_url,
                api_key=settings.zep_api_key
            )
            
            self.is_initialized = True
            logger.info("✅ Zep service initialized successfully")
            
        except ImportError:
            logger.warning("⚠️ Zep client not available, service will be disabled")
            self.client = None
            self.is_initialized = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Zep service: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup Zep service resources."""
        try:
            if self.client:
                self.client = None
            self.is_initialized = False
            logger.info("✅ Zep service cleaned up successfully")
        except Exception as e:
            logger.error(f"❌ Error during Zep cleanup: {e}")
    
    async def store_message(
        self,
        session_id: str,
        message: ChatMessage,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Store a message in Zep memory.
        
        Args:
            session_id: Session identifier
            message: Chat message to store
            user_id: User identifier
            
        Returns:
            Success status
        """
        if not self.is_initialized or not self.client:
            logger.warning("Zep service not available, skipping message storage")
            return False
        
        try:
            # Create message for Zep
            zep_message = {
                "role": message.role.value,
                "content": message.content,
                "metadata": message.metadata or {}
            }
            
            # Store in Zep
            await self.client.memory.add_memory(
                session_id=session_id,
                messages=[zep_message],
                user_id=user_id
            )
            
            logger.info(f"Stored message in Zep for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing message in Zep: {e}")
            return False
    
    async def get_memory_context(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> MemoryContext:
        """
        Get memory context from Zep.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            limit: Maximum number of memories to retrieve
            
        Returns:
            Memory context with facts and relationships
        """
        if not self.is_initialized:
            raise RuntimeError("Zep service not initialized")
        
        try:
            # Get memory from Zep
            memory = await self.client.memory.get_memory(
                session_id=session_id,
                user_id=user_id,
                limit=limit
            )
            
            # Convert to our memory context format
            context = MemoryContext(
                session_id=session_id,
                user_id=user_id
            )
            
            # Extract facts from memory
            if memory.messages:
                for msg in memory.messages:
                    if msg.role == MessageRole.USER.value:
                        # Extract facts from user messages
                        facts = await self._extract_facts_from_message(msg.content)
                        for fact_content in facts:
                            fact = MemoryFact(
                                content=fact_content,
                                source=MemorySource.ZEP,
                                priority=MemoryPriority.MEDIUM,
                                confidence=0.8
                            )
                            context.facts.append(fact)
            
            # Extract relationships from memory
            if hasattr(memory, 'relationships') and memory.relationships:
                for rel in memory.relationships:
                    relationship = MemoryRelationship(
                        source_entity=rel.source,
                        target_entity=rel.target,
                        relationship_type=rel.relationship_type,
                        source=MemorySource.ZEP,
                        confidence=rel.confidence or 0.8
                    )
                    context.relationships.append(relationship)
            
            # Generate context summary
            if context.facts or context.relationships:
                context.context_summary = await self._generate_context_summary(context)
            
            logger.info(f"Retrieved memory context from Zep for session {session_id}")
            return context
            
        except Exception as e:
            logger.error(f"❌ Error getting memory context from Zep: {e}")
            return MemoryContext(session_id=session_id, user_id=user_id)
    
    async def search_memory(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryFact]:
        """
        Search memory using Zep.
        
        Args:
            query: Search query
            session_id: Session identifier (optional)
            user_id: User identifier (optional)
            limit: Maximum number of results
            
        Returns:
            List of relevant memory facts
        """
        if not self.is_initialized:
            raise RuntimeError("Zep service not initialized")
        
        try:
            # Search memory in Zep
            search_results = await self.client.memory.search_memory(
                text=query,
                session_id=session_id,
                user_id=user_id,
                limit=limit
            )
            
            # Convert to our format
            facts = []
            for result in search_results:
                fact = MemoryFact(
                    content=result.content,
                    source=MemorySource.ZEP,
                    priority=MemoryPriority.MEDIUM,
                    confidence=result.score or 0.8,
                    metadata={"zep_score": result.score}
                )
                facts.append(fact)
            
            logger.info(f"Found {len(facts)} memory results for query: {query}")
            return facts
            
        except Exception as e:
            logger.error(f"❌ Error searching memory in Zep: {e}")
            return []
    
    async def create_relationship(
        self,
        source_entity: str,
        target_entity: str,
        relationship_type: str,
        session_id: Optional[str] = None,
        confidence: float = 0.8
    ) -> MemoryRelationship:
        """
        Create a relationship in Zep memory.
        
        Args:
            source_entity: Source entity
            target_entity: Target entity
            relationship_type: Type of relationship
            session_id: Session identifier
            confidence: Confidence score
            
        Returns:
            Created relationship
        """
        if not self.is_initialized:
            raise RuntimeError("Zep service not initialized")
        
        try:
            # Create relationship in Zep
            relationship = await self.client.create_relationship(
                source=source_entity,
                target=target_entity,
                relationship_type=relationship_type,
                session_id=session_id,
                confidence=confidence
            )
            
            # Convert to our format
            memory_relationship = MemoryRelationship(
                source_entity=source_entity,
                target_entity=target_entity,
                relationship_type=relationship_type,
                source=MemorySource.ZEP,
                confidence=confidence
            )
            
            logger.info(f"Created relationship in Zep: {source_entity} -> {target_entity}")
            return memory_relationship
            
        except Exception as e:
            logger.error(f"❌ Error creating relationship in Zep: {e}")
            raise
    
    async def get_session_summary(self, session_id: str) -> Optional[str]:
        """
        Get session summary from Zep.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary or None
        """
        if not self.is_initialized:
            raise RuntimeError("Zep service not initialized")
        
        try:
            # Get session summary from Zep
            summary = await self.client.memory.get_session_summary(session_id=session_id)
            return summary.summary if summary else None
            
        except Exception as e:
            logger.error(f"❌ Error getting session summary from Zep: {e}")
            return None
    
    async def _extract_facts_from_message(self, message_content: str) -> List[str]:
        """Extract facts from a message using simple heuristics."""
        # Simple fact extraction - in production, use more sophisticated NLP
        facts = []
        
        # Look for statements that might be facts
        sentences = message_content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                # Simple heuristic: statements with "is", "are", "was", "were"
                fact_indicators = ["is", "are", "was", "were", "like", "prefer", "want"]
                if any(indicator in sentence.lower() for indicator in fact_indicators):
                    facts.append(sentence)
        
        return facts
    
    async def _generate_context_summary(self, context: MemoryContext) -> str:
        """Generate a summary of the memory context."""
        summary_parts = []
        
        if context.facts:
            fact_count = len(context.facts)
            summary_parts.append(f"{fact_count} facts stored")
        
        if context.relationships:
            rel_count = len(context.relationships)
            summary_parts.append(f"{rel_count} relationships tracked")
        
        return "; ".join(summary_parts) if summary_parts else "No memory context"


 