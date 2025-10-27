# ============================================================================
# File: rag_anything/retrieval/hybrid_retriever.py
# ============================================================================
"""Hybrid retrieval combining vector and graph search."""

from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class HybridRetriever:
    """Combines vector similarity and knowledge graph retrieval."""
    
    def __init__(self, lightrag_instance=None, alpha: float = 0.7):
        """Initialize hybrid retriever.
        
        Args:
            lightrag_instance: LightRAG instance for queries
            alpha: Weight for vector vs graph (0=graph only, 1=vector only)
        """
        self.lightrag = lightrag_instance
        self.alpha = alpha
        self.logger = logger.bind(component="hybrid_retriever")
    
    async def retrieve(
        self, 
        query_text: str, 
        mode: str = "hybrid",
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Retrieve relevant context using hybrid approach.
        
        Args:
            query: Query string
            mode: Retrieval mode (hybrid, naive, local, global)
            top_k: Number of results
            
        Returns:
            Retrieved context with metadata
        """
        if not self.lightrag:
            self.logger.error("lightrag_not_initialized")
            return {"context": "", "sources": [], "error": "Not initialized"}
        
        try:
            from lightrag.base import QueryParam
            
            query_param = QueryParam(
                mode=mode,
                only_need_context=False,
                stream=False,
                top_k=top_k
            )
            
            result = await self.lightrag.aquery(query_text, param=query_param)

            print("👀👀👀👀👀👀👀👀👀👀👀👀👀👀") ######################################################################################### testing instruction
            print(result) ######################################################################################### testing instruction
            print("👀👀👀👀👀👀👀👀👀👀👀👀👀👀") ######################################################################################### testing instruction
            
            # Extract content
            if hasattr(result, 'content'):
                context = result.content
                
                if context is None and hasattr(result, 'response_iterator'):
                    chunks = []
                    async for chunk in result.response_iterator:
                        chunks.append(chunk)
                    context = ''.join(chunks)
            else:
                context = str(result)
            
            return {
                "context": context or "",
                "sources": [],  # TODO: Extract from result
                "mode": mode,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error("retrieval_failed", error=str(e))
            return {
                "context": "",
                "sources": [],
                "error": str(e),
                "status": "failed"
            }
    
    async def retrieve_with_scores(
        self,
        query_text: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve with relevance scores.
        
        Args:
            query: Query string
            top_k: Number of results
            
        Returns:
            List of results with scores
        """
        # Placeholder for scored retrieval
        return []