"""RAG Engine Agent for orchestrating knowledge retrieval."""
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import structlog

from src.agents.base import BaseAgent, AgentRequest
from src.rag_anything.client import RAGAnythingClient
from src.rag_anything.config import RAGConfig
from .prompts import (
    SYSTEM_PROMPT,
    CONTEXT_SYNTHESIS_PROMPT,
    RERANKING_PROMPT,
    ENTITY_EXTRACTION_PROMPT,
)
from .retrieval_manager import RetrievalManager
from .context_merger import ContextMerger

logger = structlog.get_logger(__name__)


class RAGEngineAgent(BaseAgent):
    """Agent for orchestrating RAG retrieval and context synthesis.

    Uses Claude-4 Sonnet to:
    - Coordinate hybrid retrieval (vector + knowledge graph)
    - Rerank and filter retrieved content
    - Synthesize coherent context from multiple sources
    - Extract financial entities and relationships
    - Manage source attribution
    """

    def __init__(self, rag_client: Optional[RAGAnythingClient] = None):
        """Initialize RAG Engine Agent.

        Args:
            rag_client: Optional RAG client (creates default if not provided)
        """
        super().__init__(agent_name="rag_engine")

        # Initialize RAG client
        if rag_client is None:
            rag_config = RAGConfig()
            self.rag_client = RAGAnythingClient(config=rag_config)
        else:
            self.rag_client = rag_client

        self.retrieval_manager = RetrievalManager(self.rag_client)
        self.context_merger = ContextMerger()
        self.logger = logger.bind(agent="rag_engine")

    async def initialize(self) -> None:
        """Initialize RAG system.

        This should be called before first use.
        """
        await self.rag_client.initialize()
        self.logger.info("rag_engine_initialized")

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute RAG engine logic.

        Args:
            request: Agent request with query context

        Returns:
            Retrieved context with sources and entities
        """
        # Extract query context from request
        query_output = request.context.get("query_output", {}) if request.context else {}

        if not query_output:
            self.logger.warning("no_query_context", using_fallback=True)
            query_output = {
                "query_context": {"primary_focus": request.user_input},
                "entities": {},
                "search_strategy": {"vector_weight": 0.7, "graph_weight": 0.3},
            }

        # Extract documents from context
        documents = request.context.get("documents", []) if request.context else []

        # Step 1: Retrieve from RAG system
        retrieved_docs = await self._retrieve_documents(query_output, documents)

        # Step 2: Rerank by relevance
        reranked_docs = await self._rerank_documents(
            query_output.get("query_context", {}),
            retrieved_docs
        )

        # Step 3: Synthesize context
        synthesized = await self._synthesize_context(
            query_output,
            reranked_docs
        )

        # Step 4: Extract entities and relationships
        entities = await self._extract_entities(synthesized.get("retrieved_context", ""))

        # Merge entities
        synthesized["entities"] = entities
        synthesized["knowledge_graph_entities"] = list(entities.keys())

        self.logger.info(
            "rag_retrieval_complete",
            sources_count=len(synthesized.get("sources", [])),
            findings_count=len(synthesized.get("key_findings", [])),
            context_length=len(synthesized.get("retrieved_context", "")),
        )

        return synthesized

    async def _retrieve_documents(
        self,
        query_output: Dict[str, Any],
        documents: List[Path]
    ) -> List[Dict[str, Any]]:
        """Retrieve documents from RAG system.

        Args:
            query_output: Query analysis from Query Agent
            documents: Optional list of document paths to process

        Returns:
            List of retrieved document chunks with context
        """
        # If documents provided, process them first
        if documents:
            await self._process_documents(documents)

        # Build query from query_output
        query_text = self._build_query_text(query_output)

        # Determine search mode
        search_strategy = query_output.get("search_strategy", {})
        mode = self._determine_search_mode(search_strategy)

        self.logger.info(
            "retrieving_documents",
            query_length=len(query_text),
            mode=mode,
            has_documents=bool(documents)
        )

        # Execute retrieval using RAG-Anything
        try:
            result = await self.rag_client.query(
                query_text=query_text,
                mode=mode,
                top_k=10,
            )

            # Extract context from result
            context = result.get("context", "")
            sources = result.get("sources", [])

            # Convert to document chunks format
            if context:
                # Split context into chunks if it's a long string
                chunks = []
                if len(context) > 1000:
                    # Split by paragraphs
                    paragraphs = context.split("\n\n")
                    for i, para in enumerate(paragraphs):
                        if para.strip():
                            chunks.append({
                                "id": f"chunk_{i}",
                                "content": para.strip(),
                                "source": sources[0] if sources else "unknown",
                                "score": 1.0 / (i + 1)  # Descending relevance
                            })
                else:
                    chunks.append({
                        "id": "chunk_0",
                        "content": context,
                        "source": sources[0] if sources else "unknown",
                        "score": 1.0
                    })

                self.logger.info(
                    "retrieval_successful",
                    chunks_retrieved=len(chunks),
                    total_context_length=len(context)
                )

                return chunks
            else:
                self.logger.warning("no_context_retrieved", query=query_text)
                return []

        except Exception as e:
            self.logger.error("retrieval_failed", error=str(e), error_type=type(e).__name__)
            # Return empty results
            return []

    async def _process_documents(self, documents: List[Path]) -> None:
        """Process and ingest documents into RAG system.

        Args:
            documents: List of document paths
        """
        self.logger.info("processing_documents", count=len(documents))

        for doc_path in documents:
            try:
                await self.rag_client.process_document(doc_path)
            except Exception as e:
                self.logger.error(
                    "document_processing_failed",
                    document=str(doc_path),
                    error=str(e),
                )

    async def _rerank_documents(
        self,
        query_context: Dict[str, Any],
        retrieved_docs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rerank retrieved documents using Claude.

        Args:
            query_context: Query context
            retrieved_docs: Retrieved documents

        Returns:
            Reranked documents
        """
        if not retrieved_docs:
            return []

        # Build reranking prompt
        chunks_str = json.dumps(retrieved_docs[:20], indent=2)  # Top 20 only

        prompt = RERANKING_PROMPT.format(
            query=str(query_context),
            chunks=chunks_str
        )

        try:
            response = await self.claude_client.generate(
                user_message=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.2,  # Deterministic for ranking
                max_tokens=2048,
            )

            reranked = self._parse_json_response(response)

            # Map back to original documents
            reranked_docs = []
            for item in reranked.get("reranked_chunks", [])[:10]:  # Top 10
                chunk_id = item.get("chunk_id")
                # Find original doc (simplified - would use actual IDs)
                for doc in retrieved_docs:
                    if str(doc.get("id", "")) == str(chunk_id):
                        reranked_docs.append(doc)
                        break

            return reranked_docs if reranked_docs else retrieved_docs[:10]

        except Exception as e:
            self.logger.error("reranking_failed", error=str(e))
            return retrieved_docs[:10]

    async def _synthesize_context(
        self,
        query_output: Dict[str, Any],
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize coherent context from retrieved documents.

        Args:
            query_output: Query analysis
            documents: Retrieved and reranked documents

        Returns:
            Synthesized context dictionary
        """
        # Build synthesis prompt
        docs_str = json.dumps(documents, indent=2)
        entities_str = json.dumps(query_output.get("entities", {}), indent=2)
        query_context_str = json.dumps(query_output.get("query_context", {}), indent=2)

        prompt = CONTEXT_SYNTHESIS_PROMPT.format(
            query_context=query_context_str,
            documents=docs_str,
            entities=entities_str
        )

        try:
            response = await self.claude_client.generate(
                user_message=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.5,  # Balanced for synthesis
                max_tokens=4096,
            )

            synthesized = self._parse_json_response(response)

            # Add relevance scores
            synthesized["relevance_scores"] = self._calculate_relevance_scores(documents)

            return synthesized

        except Exception as e:
            self.logger.error("synthesis_failed", error=str(e))
            return self._get_fallback_context(documents)

    async def _extract_entities(self, context: str) -> Dict[str, List[str]]:
        """Extract entities and relationships from context.

        Args:
            context: Synthesized context

        Returns:
            Entities dictionary
        """
        if not context:
            return {}

        prompt = ENTITY_EXTRACTION_PROMPT.format(context=context)

        try:
            response = await self.claude_client.generate(
                user_message=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1024,
            )

            entities = self._parse_json_response(response)
            return entities

        except Exception as e:
            self.logger.error("entity_extraction_failed", error=str(e))
            return {}

    def _build_query_text(self, query_output: Dict[str, Any]) -> str:
        """Build query text from query output.

        Args:
            query_output: Query analysis

        Returns:
            Query string
        """
        query_context = query_output.get("query_context", {})
        entities = query_output.get("entities", {})

        # Build natural language query
        parts = [query_context.get("primary_focus", "")]

        # Add entities
        for entity_type, entity_values in entities.items():
            if entity_values:
                parts.append(f"{entity_type}: {', '.join(entity_values[:3])}")

        return " ".join(filter(None, parts))

    def _determine_search_mode(self, search_strategy: Dict[str, Any]) -> str:
        """Determine search mode from strategy.

        Args:
            search_strategy: Search strategy dict

        Returns:
            Search mode string
        """
        vector_weight = search_strategy.get("vector_weight", 0.7)
        graph_weight = search_strategy.get("graph_weight", 0.3)

        if vector_weight > 0.8:
            return "vector"
        elif graph_weight > 0.8:
            return "graph"
        else:
            return "hybrid"

    def _calculate_relevance_scores(
        self,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate relevance scores for documents.

        Args:
            documents: Retrieved documents

        Returns:
            Relevance scores dictionary
        """
        scores = {}
        for i, doc in enumerate(documents):
            doc_id = doc.get("id", f"doc_{i}")
            # Use existing score or calculate based on rank
            score = doc.get("score", 1.0 / (i + 1))
            scores[doc_id] = score

        return scores

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from Claude response."""
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()

        return json.loads(json_str)

    def _get_fallback_context(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get fallback context when synthesis fails.

        Args:
            documents: Retrieved documents

        Returns:
            Fallback context dictionary
        """
        # Simple concatenation of top documents
        context_parts = []
        sources = []

        for doc in documents[:5]:
            content = doc.get("content", doc.get("text", ""))
            if content:
                context_parts.append(content)

            source = doc.get("source", doc.get("document", "unknown"))
            if source not in sources:
                sources.append(source)

        return {
            "retrieved_context": "\n\n".join(context_parts),
            "sources": sources,
            "key_findings": [],
            "metrics": {},
            "relevance_scores": self._calculate_relevance_scores(documents),
        }
