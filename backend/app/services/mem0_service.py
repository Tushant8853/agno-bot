"""
Mem0 memory service for scalable long-term memory with fact extraction.
"""

import asyncio
import time
import json
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


class Mem0Service:
    """Service for interacting with Mem0 memory system."""
    
    def __init__(self):
        self.client = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the Mem0 service."""
        try:
            # Import Mem0 client
            from mem0 import Mem0Client
            
            # Initialize Mem0 client
            self.client = Mem0Client(
                api_key=settings.mem0_api_key,
                base_url=settings.mem0_base_url
            )
            
            self.is_initialized = True
            logger.info("✅ Mem0 service initialized successfully")
            
        except ImportError:
            logger.warning("⚠️ Mem0 client not available, using mock implementation")
            self.client = MockMem0Client()
            self.is_initialized = True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Mem0 service: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup Mem0 service resources."""
        try:
            if self.client:
                self.client = None
            self.is_initialized = False
            logger.info("✅ Mem0 service cleaned up successfully")
        except Exception as e:
            logger.error(f"❌ Error during Mem0 cleanup: {e}")
    
    async def extract_facts(
        self,
        text: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[MemoryFact]:
        """
        Extract facts from text using Mem0's extraction pipeline.
        
        Args:
            text: Text to extract facts from
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            List of extracted facts
        """
        if not self.is_initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            # Use Mem0's fact extraction
            extraction_result = await self.client.extract_facts(
                text=text,
                session_id=session_id,
                user_id=user_id
            )
            
            # Convert to our format
            facts = []
            for fact_data in extraction_result.facts:
                fact = MemoryFact(
                    content=fact_data.content,
                    source=MemorySource.MEM0,
                    priority=self._map_priority(fact_data.priority),
                    confidence=fact_data.confidence,
                    metadata={
                        "mem0_id": fact_data.id,
                        "extraction_method": fact_data.method,
                        "entities": fact_data.entities
                    },
                    tags=fact_data.tags or []
                )
                facts.append(fact)
            
            logger.info(f"Extracted {len(facts)} facts using Mem0")
            return facts
            
        except Exception as e:
            logger.error(f"❌ Error extracting facts with Mem0: {e}")
            return []
    
    async def store_facts(
        self,
        facts: List[MemoryFact],
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Store facts in Mem0 memory.
        
        Args:
            facts: List of facts to store
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Success status
        """
        if not self.is_initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            # Convert to Mem0 format
            mem0_facts = []
            for fact in facts:
                mem0_fact = {
                    "content": fact.content,
                    "confidence": fact.confidence,
                    "priority": fact.priority.value,
                    "metadata": fact.metadata or {},
                    "tags": fact.tags
                }
                mem0_facts.append(mem0_fact)
            
            # Store in Mem0
            await self.client.store_facts(
                facts=mem0_facts,
                session_id=session_id,
                user_id=user_id
            )
            
            logger.info(f"Stored {len(facts)} facts in Mem0")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing facts in Mem0: {e}")
            return False
    
    async def retrieve_facts(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryFact]:
        """
        Retrieve facts from Mem0 memory.
        
        Args:
            query: Search query
            session_id: Session identifier
            user_id: User identifier
            limit: Maximum number of results
            
        Returns:
            List of relevant facts
        """
        if not self.is_initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            # Retrieve from Mem0
            retrieval_result = await self.client.retrieve_facts(
                query=query,
                session_id=session_id,
                user_id=user_id,
                limit=limit
            )
            
            # Convert to our format
            facts = []
            for fact_data in retrieval_result.facts:
                fact = MemoryFact(
                    content=fact_data.content,
                    source=MemorySource.MEM0,
                    priority=self._map_priority(fact_data.priority),
                    confidence=fact_data.confidence,
                    metadata={
                        "mem0_id": fact_data.id,
                        "relevance_score": fact_data.relevance_score,
                        "last_accessed": fact_data.last_accessed
                    },
                    tags=fact_data.tags or []
                )
                facts.append(fact)
            
            logger.info(f"Retrieved {len(facts)} facts from Mem0 for query: {query}")
            return facts
            
        except Exception as e:
            logger.error(f"❌ Error retrieving facts from Mem0: {e}")
            return []
    
    async def consolidate_facts(
        self,
        facts: List[MemoryFact],
        session_id: Optional[str] = None
    ) -> List[MemoryFact]:
        """
        Consolidate similar facts using Mem0's consolidation pipeline.
        
        Args:
            facts: List of facts to consolidate
            session_id: Session identifier
            
        Returns:
            List of consolidated facts
        """
        if not self.is_initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            # Convert to Mem0 format
            mem0_facts = []
            for fact in facts:
                mem0_fact = {
                    "content": fact.content,
                    "confidence": fact.confidence,
                    "priority": fact.priority.value,
                    "metadata": fact.metadata or {}
                }
                mem0_facts.append(mem0_fact)
            
            # Consolidate using Mem0
            consolidation_result = await self.client.consolidate_facts(
                facts=mem0_facts,
                session_id=session_id
            )
            
            # Convert back to our format
            consolidated_facts = []
            for fact_data in consolidation_result.consolidated_facts:
                fact = MemoryFact(
                    content=fact_data.content,
                    source=MemorySource.MEM0,
                    priority=self._map_priority(fact_data.priority),
                    confidence=fact_data.confidence,
                    metadata={
                        "mem0_id": fact_data.id,
                        "consolidation_method": fact_data.method,
                        "source_facts": fact_data.source_facts
                    }
                )
                consolidated_facts.append(fact)
            
            logger.info(f"Consolidated {len(facts)} facts into {len(consolidated_facts)} facts")
            return consolidated_facts
            
        except Exception as e:
            logger.error(f"❌ Error consolidating facts with Mem0: {e}")
            return facts
    
    async def get_memory_analytics(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get memory analytics from Mem0.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Memory analytics data
        """
        if not self.is_initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            # Get analytics from Mem0
            analytics = await self.client.get_analytics(
                user_id=user_id,
                session_id=session_id
            )
            
            return {
                "total_facts": analytics.total_facts,
                "total_relationships": analytics.total_relationships,
                "memory_usage_bytes": analytics.memory_usage,
                "average_confidence": analytics.average_confidence,
                "source_distribution": analytics.source_distribution,
                "priority_distribution": analytics.priority_distribution,
                "consolidation_events": analytics.consolidation_events
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting analytics from Mem0: {e}")
            return {}
    
    async def process_message(
        self,
        message: ChatMessage,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[MemoryFact]:
        """
        Process a message through Mem0's extraction pipeline.
        
        Args:
            message: Chat message to process
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            List of extracted facts
        """
        if not self.is_initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            # Extract facts from message
            facts = await self.extract_facts(
                text=message.content,
                session_id=session_id,
                user_id=user_id
            )
            
            # Store facts
            if facts:
                await self.store_facts(
                    facts=facts,
                    session_id=session_id,
                    user_id=user_id
                )
            
            logger.info(f"Processed message through Mem0, extracted {len(facts)} facts")
            return facts
            
        except Exception as e:
            logger.error(f"❌ Error processing message with Mem0: {e}")
            return []
    
    def _map_priority(self, mem0_priority: str) -> MemoryPriority:
        """Map Mem0 priority to our priority enum."""
        priority_mapping = {
            "low": MemoryPriority.LOW,
            "medium": MemoryPriority.MEDIUM,
            "high": MemoryPriority.HIGH,
            "critical": MemoryPriority.CRITICAL
        }
        return priority_mapping.get(mem0_priority.lower(), MemoryPriority.MEDIUM)


class MockMem0Client:
    """Mock Mem0 client for development/testing."""
    
    def __init__(self):
        self.facts = []
        self.analytics = {
            "total_facts": 0,
            "total_relationships": 0,
            "memory_usage": 0,
            "average_confidence": 0.8,
            "source_distribution": {"mem0": 0},
            "priority_distribution": {"medium": 0},
            "consolidation_events": 0
        }
    
    async def extract_facts(self, text: str, session_id: Optional[str] = None, user_id: Optional[str] = None):
        class MockFact:
            def __init__(self, content, confidence=0.8):
                self.content = content
                self.confidence = confidence
                self.id = f"fact_{len(self.facts)}"
                self.priority = "medium"
                self.method = "heuristic"
                self.entities = []
                self.tags = []
        
        class MockExtractionResult:
            def __init__(self, facts):
                self.facts = facts
        
        # Simple fact extraction
        facts = []
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                fact_indicators = ["is", "are", "was", "were", "like", "prefer", "want"]
                if any(indicator in sentence.lower() for indicator in fact_indicators):
                    facts.append(MockFact(sentence))
        
        return MockExtractionResult(facts)
    
    async def store_facts(self, facts: List[Dict], session_id: Optional[str] = None, user_id: Optional[str] = None):
        self.facts.extend(facts)
        self.analytics["total_facts"] = len(self.facts)
    
    async def retrieve_facts(self, query: str, session_id: Optional[str] = None, user_id: Optional[str] = None, limit: int = 10):
        class MockFact:
            def __init__(self, content, confidence=0.8):
                self.content = content
                self.confidence = confidence
                self.id = f"fact_{len(self.facts)}"
                self.priority = "medium"
                self.relevance_score = 0.8
                self.last_accessed = datetime.utcnow()
                self.tags = []
        
        class MockRetrievalResult:
            def __init__(self, facts):
                self.facts = facts
        
        # Simple search
        results = []
        for fact in self.facts:
            if query.lower() in fact.get('content', '').lower():
                results.append(MockFact(fact['content'], fact.get('confidence', 0.8)))
        
        return MockRetrievalResult(results[:limit])
    
    async def consolidate_facts(self, facts: List[Dict], session_id: Optional[str] = None):
        class MockFact:
            def __init__(self, content, confidence=0.8):
                self.content = content
                self.confidence = confidence
                self.id = f"consolidated_{len(self.facts)}"
                self.priority = "medium"
                self.method = "similarity"
                self.source_facts = []
        
        class MockConsolidationResult:
            def __init__(self, consolidated_facts):
                self.consolidated_facts = consolidated_facts
        
        # Simple consolidation (just return unique facts)
        unique_facts = []
        seen_contents = set()
        
        for fact in facts:
            content = fact.get('content', '')
            if content not in seen_contents:
                unique_facts.append(MockFact(content, fact.get('confidence', 0.8)))
                seen_contents.add(content)
        
        self.analytics["consolidation_events"] += 1
        return MockConsolidationResult(unique_facts)
    
    async def get_analytics(self, user_id: Optional[str] = None, session_id: Optional[str] = None):
        class MockAnalytics:
            def __init__(self, data):
                self.total_facts = data["total_facts"]
                self.total_relationships = data["total_relationships"]
                self.memory_usage = data["memory_usage"]
                self.average_confidence = data["average_confidence"]
                self.source_distribution = data["source_distribution"]
                self.priority_distribution = data["priority_distribution"]
                self.consolidation_events = data["consolidation_events"]
        
        return MockAnalytics(self.analytics) 