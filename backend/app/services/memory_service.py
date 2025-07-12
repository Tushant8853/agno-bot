"""
Hybrid memory service that coordinates between Zep and Mem0 memory systems.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import structlog

from app.config import settings
from app.models.memory import (
    MemoryFact, 
    MemoryRelationship, 
    MemoryContext, 
    MemoryQuery,
    MemorySearchResult,
    MemoryConsolidation,
    MemoryAnalytics,
    MemorySource,
    MemoryPriority
)
from app.models.chat import ChatMessage, MessageRole
from app.services.zep_service import ZepService
from app.services.mem0_service import Mem0Service

logger = structlog.get_logger()


class MemoryService:
    """Hybrid memory service coordinating Zep and Mem0."""
    
    def __init__(self):
        self.zep_service = ZepService()
        self.mem0_service = Mem0Service()
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the hybrid memory service."""
        try:
            # Initialize both memory services
            await self.zep_service.initialize()
            await self.mem0_service.initialize()
            
            self.is_initialized = True
            logger.info("✅ Hybrid memory service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize hybrid memory service: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup memory service resources."""
        try:
            await self.zep_service.cleanup()
            await self.mem0_service.cleanup()
            self.is_initialized = False
            logger.info("✅ Hybrid memory service cleaned up successfully")
        except Exception as e:
            logger.error(f"❌ Error during memory service cleanup: {e}")
    
    async def process_message(
        self,
        message: ChatMessage,
        session_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a message through both memory systems.
        
        Args:
            message: Chat message to process
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Processing results from both systems
        """
        if not self.is_initialized:
            raise RuntimeError("Memory service not initialized")
        
        start_time = time.time()
        
        try:
            # Process in parallel
            zep_task = self.zep_service.store_message(session_id, message, user_id)
            mem0_task = self.mem0_service.process_message(message, session_id, user_id)
            
            zep_result, mem0_facts = await asyncio.gather(zep_task, mem0_task)
            
            # Consolidate facts if we have multiple
            consolidated_facts = []
            if mem0_facts:
                consolidated_facts = await self.mem0_service.consolidate_facts(
                    mem0_facts, session_id
                )
            
            processing_time = time.time() - start_time
            
            result = {
                "zep_stored": zep_result,
                "mem0_facts_extracted": len(mem0_facts),
                "mem0_facts_consolidated": len(consolidated_facts),
                "processing_time_ms": round(processing_time * 1000, 2)
            }
            
            logger.info(
                "Processed message through hybrid memory",
                session_id=session_id,
                zep_stored=zep_result,
                mem0_facts=len(mem0_facts),
                consolidated_facts=len(consolidated_facts)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing message through hybrid memory: {e}")
            raise
    
    async def get_memory_context(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        query: Optional[str] = None
    ) -> MemoryContext:
        """
        Get comprehensive memory context from both systems.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            query: Optional query for context retrieval
            
        Returns:
            Combined memory context
        """
        if not self.is_initialized:
            raise RuntimeError("Memory service not initialized")
        
        try:
            # Get context from both systems
            zep_context = await self.zep_service.get_memory_context(
                session_id, user_id
            )
            
            # Get relevant facts from Mem0
            mem0_facts = []
            if query:
                mem0_facts = await self.mem0_service.retrieve_facts(
                    query, session_id, user_id
                )
            
            # Combine contexts
            combined_context = MemoryContext(
                session_id=session_id,
                user_id=user_id
            )
            
            # Add Zep facts and relationships
            combined_context.facts.extend(zep_context.facts)
            combined_context.relationships.extend(zep_context.relationships)
            
            # Add Mem0 facts
            combined_context.facts.extend(mem0_facts)
            
            # Generate combined summary
            if combined_context.facts or combined_context.relationships:
                combined_context.context_summary = await self._generate_combined_summary(
                    combined_context
                )
            
            logger.info(
                "Retrieved hybrid memory context",
                session_id=session_id,
                total_facts=len(combined_context.facts),
                total_relationships=len(combined_context.relationships)
            )
            
            return combined_context
            
        except Exception as e:
            logger.error(f"❌ Error getting hybrid memory context: {e}")
            return MemoryContext(session_id=session_id, user_id=user_id)
    
    async def search_memory(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> MemorySearchResult:
        """
        Search memory across both systems with intelligent routing.
        
        Args:
            query: Search query
            session_id: Session identifier
            user_id: User identifier
            limit: Maximum number of results
            
        Returns:
            Search results from both systems
        """
        if not self.is_initialized:
            raise RuntimeError("Memory service not initialized")
        
        start_time = time.time()
        
        try:
            # Determine which system to use based on query type
            query_type = self._classify_query(query)
            
            if query_type == "relationship":
                # Use Zep for relationship queries
                zep_facts = await self.zep_service.search_memory(
                    query, session_id, user_id, limit
                )
                mem0_facts = []
            elif query_type == "fact":
                # Use Mem0 for fact queries
                mem0_facts = await self.mem0_service.retrieve_facts(
                    query, session_id, user_id, limit
                )
                zep_facts = []
            else:
                # Use both systems for general queries
                zep_task = self.zep_service.search_memory(query, session_id, user_id, limit // 2)
                mem0_task = self.mem0_service.retrieve_facts(query, session_id, user_id, limit // 2)
                
                zep_facts, mem0_facts = await asyncio.gather(zep_task, mem0_task)
            
            # Combine and rank results
            all_results = zep_facts + mem0_facts
            ranked_results = self._rank_results(all_results, query)
            
            search_time = time.time() - start_time
            
            result = MemorySearchResult(
                query=query,
                results=ranked_results[:limit],
                total_count=len(ranked_results),
                search_time_ms=round(search_time * 1000, 2),
                metadata={
                    "query_type": query_type,
                    "zep_results": len(zep_facts),
                    "mem0_results": len(mem0_facts)
                }
            )
            
            logger.info(
                "Searched hybrid memory",
                query=query,
                query_type=query_type,
                total_results=len(ranked_results),
                search_time_ms=result.search_time_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error searching hybrid memory: {e}")
            return MemorySearchResult(
                query=query,
                results=[],
                total_count=0,
                search_time_ms=0
            )
    
    async def create_relationship(
        self,
        source_entity: str,
        target_entity: str,
        relationship_type: str,
        session_id: Optional[str] = None,
        confidence: float = 0.8
    ) -> MemoryRelationship:
        """
        Create a relationship using Zep (primary for relationships).
        
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
            raise RuntimeError("Memory service not initialized")
        
        try:
            # Use Zep for relationships
            relationship = await self.zep_service.create_relationship(
                source_entity, target_entity, relationship_type, session_id, confidence
            )
            
            logger.info(f"Created relationship: {source_entity} -> {target_entity}")
            return relationship
            
        except Exception as e:
            logger.error(f"❌ Error creating relationship: {e}")
            raise
    
    async def get_memory_analytics(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> MemoryAnalytics:
        """
        Get analytics from both memory systems.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Combined memory analytics
        """
        if not self.is_initialized:
            raise RuntimeError("Memory service not initialized")
        
        try:
            # Get analytics from both systems
            mem0_analytics = await self.mem0_service.get_memory_analytics(user_id, session_id)
            
            # For now, use Mem0 analytics as primary
            # In production, you'd combine analytics from both systems
            analytics = MemoryAnalytics(
                total_facts=mem0_analytics.get("total_facts", 0),
                total_relationships=mem0_analytics.get("total_relationships", 0),
                memory_usage_bytes=mem0_analytics.get("memory_usage_bytes", 0),
                average_confidence=mem0_analytics.get("average_confidence", 0.8),
                source_distribution=mem0_analytics.get("source_distribution", {}),
                priority_distribution=mem0_analytics.get("priority_distribution", {})
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting memory analytics: {e}")
            return MemoryAnalytics(
                total_facts=0,
                total_relationships=0,
                memory_usage_bytes=0,
                average_confidence=0.0,
                source_distribution={},
                priority_distribution={}
            )
    

    
    def _classify_query(self, query: str) -> str:
        """Classify query type for intelligent routing."""
        query_lower = query.lower()
        
        # Relationship indicators
        relationship_indicators = [
            "relationship", "connection", "between", "related to", "linked to",
            "associated with", "connected to", "interacts with"
        ]
        
        # Fact indicators
        fact_indicators = [
            "fact", "information", "detail", "preference", "like", "dislike",
            "prefer", "want", "need", "remember"
        ]
        
        if any(indicator in query_lower for indicator in relationship_indicators):
            return "relationship"
        elif any(indicator in query_lower for indicator in fact_indicators):
            return "fact"
        else:
            return "general"
    
    def _rank_results(self, results: List[MemoryFact], query: str) -> List[MemoryFact]:
        """Rank search results by relevance."""
        # Simple ranking based on confidence and source
        def rank_score(fact: MemoryFact) -> float:
            score = fact.confidence
            
            # Boost Zep results for relationship queries
            if fact.source == MemorySource.ZEP:
                score += 0.1
            
            # Boost Mem0 results for fact queries
            if fact.source == MemorySource.MEM0:
                score += 0.05
            
            return score
        
        return sorted(results, key=rank_score, reverse=True)
    
    async def _generate_combined_summary(self, context: MemoryContext) -> str:
        """Generate a summary of the combined memory context."""
        summary_parts = []
        
        if context.facts:
            zep_facts = [f for f in context.facts if f.source == MemorySource.ZEP]
            mem0_facts = [f for f in context.facts if f.source == MemorySource.MEM0]
            
            if zep_facts:
                summary_parts.append(f"{len(zep_facts)} Zep facts")
            if mem0_facts:
                summary_parts.append(f"{len(mem0_facts)} Mem0 facts")
        
        if context.relationships:
            summary_parts.append(f"{len(context.relationships)} relationships")
        
        return "; ".join(summary_parts) if summary_parts else "No memory context" 