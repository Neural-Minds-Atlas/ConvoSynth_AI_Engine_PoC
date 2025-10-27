"""Retrieval Manager for RAG Engine."""
from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(__name__)


class RetrievalManager:
    """Manages document retrieval from RAG system."""

    def __init__(self, rag_client):
        """Initialize retrieval manager.

        Args:
            rag_client: RAG client instance
        """
        self.rag_client = rag_client
        self.logger = logger.bind(component="retrieval_manager")

    async def retrieve(
        self,
        query: str,
        mode: str = "hybrid",
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve documents from RAG system.

        Args:
            query: Query text
            mode: Search mode (hybrid/vector/graph)
            top_k: Number of results

        Returns:
            List of retrieved document chunks
        """
        try:
            if not self.rag_client or not self.rag_client._initialized:
                self.logger.warning("rag_client_not_initialized")
                return []

            result = await self.rag_client.query(
                query_text=query,
                mode=mode,
                top_k=top_k
            )

            return self._format_results(result)

        except Exception as e:
            self.logger.error("retrieval_failed", error=str(e))
            return []

    def _format_results(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format RAG results into standard structure.

        Args:
            result: RAG query result

        Returns:
            Formatted document chunks
        """
        chunks = []
        context = result.get("context", "")
        sources = result.get("sources", [])

        if context:
            # Split into chunks if needed
            paragraphs = context.split("\n\n")
            for i, para in enumerate(paragraphs):
                if para.strip():
                    chunks.append({
                        "id": f"chunk_{i}",
                        "content": para.strip(),
                        "source": sources[0] if sources else "unknown",
                        "score": 1.0 / (i + 1)
                    })

        return chunks
