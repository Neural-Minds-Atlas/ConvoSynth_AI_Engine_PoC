"""Context Merger for RAG Engine."""
from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(__name__)


class ContextMerger:
    """Merges and deduplicates context from multiple sources."""

    def __init__(self):
        """Initialize context merger."""
        self.logger = logger.bind(component="context_merger")

    def merge(self, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple contexts into one.

        Args:
            contexts: List of context dictionaries

        Returns:
            Merged context dictionary
        """
        if not contexts:
            return {
                "merged_context": "",
                "sources": [],
                "total_chunks": 0
            }

        # Collect all content
        all_content = []
        all_sources = set()

        for ctx in contexts:
            if isinstance(ctx, dict):
                content = ctx.get("content", str(ctx))
                all_content.append(content)

                source = ctx.get("source")
                if source:
                    all_sources.add(source)

        # Merge and deduplicate
        merged_text = "\n\n".join(filter(None, all_content))

        return {
            "merged_context": merged_text,
            "sources": list(all_sources),
            "total_chunks": len(all_content)
        }
