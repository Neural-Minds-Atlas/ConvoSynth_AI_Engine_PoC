"""RAG client with MinerU integration for document processing and retrieval."""
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import structlog

from .config import RAGConfig

logger = structlog.get_logger(__name__)


class RAGAnythingClient:
    """Client for RAG document processing and retrieval.

    Integrates:
    - MinerU parser: Multimodal PDF parsing (tables, images, equations)
    - LightRAG: Hybrid vector + knowledge graph retrieval
    - Qdrant: Vector storage
    """

    def __init__(self, config: Optional[RAGConfig] = None, model_provider: str = "cohere"):
        """Initialize RAG client.

        Args:
            config: Optional RAG configuration
            model_provider: LLM provider to use - "cohere" or "claude" (default: "cohere")
        """
        self.config = config or RAGConfig()
        self.model_provider = model_provider.lower()
        self.logger = logger.bind(component="rag_client")

        # Validate model provider
        if self.model_provider not in ["cohere", "claude"]:
            self.logger.warning(
                "invalid_model_provider",
                provider=self.model_provider,
                defaulting_to="cohere"
            )
            self.model_provider = "cohere"

        # Ensure working directory exists
        self.config.working_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self._rag = None
        self._initialized = False

        self.logger.info(
            "rag_client_created",
            working_dir=str(self.config.working_dir),
            model_provider=self.model_provider
        )

    async def initialize(self) -> None:
        """Initialize RAG system and load existing storage if available."""
        try:
            self.logger.info("initializing_rag_system")

            # Import RAG-Anything
            try:
                from raganything import RAGAnything, RAGAnythingConfig
            except ImportError as e:
                self.logger.error(
                    "raganything_not_installed",
                    error=str(e),
                    instructions="Run: pip install 'raganything[all]'"
                )
                raise ImportError(
                    "RAG-Anything not installed. Run: pip install 'raganything[all]'"
                ) from e

            # Get model functions
            embedding_func = self._get_embedding_function()
            llm_func = self._get_llm_function()
            vision_func = self._get_vision_function()

            # Check if storage already exists
            storage_exists = (
                self.config.working_dir.exists() and
                (self.config.working_dir / "kv_store_text_chunks.json").exists()
            )

            if storage_exists:
                self.logger.info(
                    "existing_storage_found",
                    working_dir=str(self.config.working_dir)
                )

            # Initialize RAG-Anything configuration
            rag_config = RAGAnythingConfig(
                working_dir=str(self.config.working_dir),
                parser="mineru",  # MinerU parser for financial docs
                parse_method="auto",
                enable_image_processing=True,
                enable_table_processing=True,
            )

            # Initialize RAG-Anything instance (loads existing data automatically)
            self._rag = RAGAnything(
                config=rag_config,
                llm_model_func=llm_func,
                vision_model_func=vision_func,
                embedding_func=embedding_func,
            )

            # Ensure LightRAG is initialized (loads existing storage)
            if hasattr(self._rag, '_ensure_lightrag_initialized'):
                await self._rag._ensure_lightrag_initialized()

            self._initialized = True
            self.logger.info("rag_system_initialized", storage_loaded=storage_exists)

        except Exception as e:
            self.logger.error("initialization_failed", error=str(e), error_type=type(e).__name__)
            self._initialized = False

    def _get_embedding_function(self) -> Callable:
        """Get embedding function for converting text to vectors.

        Returns:
            Async embedding function with required embedding_dim attribute
        """
        from lightrag.utils import wrap_embedding_func_with_attrs

        async def openai_embedding_func(
            texts: List[str],
            **kwargs
        ) -> List[List[float]]:
            """OpenAI embedding function for RAG."""
            try:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(api_key=self.config.openai_api_key)

                response = await client.embeddings.create(
                    model=self.config.embedding_model_name,
                    input=texts
                )

                return [item.embedding for item in response.data]

            except Exception as e:
                self.logger.error("embedding_failed", error=str(e))
                # Return zero vectors as fallback
                return [[0.0] * self.config.embedding_dim for _ in texts]

        # Wrap with LightRAG's wrapper to create EmbeddingFunc object
        wrapped_func = wrap_embedding_func_with_attrs(
            embedding_dim=self.config.embedding_dim
        )(openai_embedding_func)

        return wrapped_func

    def _get_llm_function(self) -> Callable:
        """Get LLM function for knowledge graph extraction and generation.

        Returns:
            Async LLM completion function with required attributes based on model_provider
        """
        if self.model_provider == "cohere":
            return self._get_cohere_llm_function()
        elif self.model_provider == "claude":
            return self._get_claude_llm_function()
        else:
            self.logger.warning("unknown_provider_defaulting_to_cohere", provider=self.model_provider)
            return self._get_cohere_llm_function()

    def _get_cohere_llm_function(self) -> Callable:
        """Get Cohere LLM function.

        Returns:
            Async Cohere completion function with required attributes
        """
        async def cohere_llm_func(
            prompt: str,
            system_prompt: Optional[str] = None,
            **kwargs
        ) -> str:
            """Cohere LLM function for RAG with reasoning capabilities."""
            try:
                import cohere

                if prompt is None:
                    self.logger.warning("llm_received_none_prompt")
                    return ""

                client = cohere.AsyncClientV2(api_key=self.config.cohere_api_key)

                # Build messages array with system prompt if provided
                messages = []
                if system_prompt:
                    messages.append({
                        "role": "system",
                        "content": system_prompt
                    })
                messages.append({
                    "role": "user",
                    "content": str(prompt)
                })

                response = await client.chat(
                    model=self.config.cohere_model,
                    messages=messages,
                    max_tokens=kwargs.get("max_tokens", 4096),
                    temperature=kwargs.get("temperature", 0.3),
                )

                return response.message.content[0].text

            except Exception as e:
                self.logger.error("cohere_llm_failed", error=str(e), error_type=type(e).__name__)
                import traceback
                self.logger.error("cohere_llm_traceback", trace=traceback.format_exc())
                return ""

        # Add required attributes for LightRAG compatibility
        cohere_llm_func.__name__ = "cohere_llm_func"
        cohere_llm_func.max_async = 8
        cohere_llm_func.max_token_size = 128000

        return cohere_llm_func

    def _get_claude_llm_function(self) -> Callable:
        """Get Claude LLM function.

        Returns:
            Async Claude completion function with required attributes
        """
        async def claude_llm_func(
            prompt: str,
            system_prompt: Optional[str] = None,
            **kwargs
        ) -> str:
            """Claude LLM function for RAG."""
            try:
                from anthropic import AsyncAnthropic

                if prompt is None:
                    self.logger.warning("llm_received_none_prompt")
                    return ""

                client = AsyncAnthropic(api_key=self.config.anthropic_api_key)

                messages = [{"role": "user", "content": str(prompt)}]

                response = await client.messages.create(
                    model=self.config.claude_model,
                    max_tokens=kwargs.get("max_tokens", 4096),
                    temperature=kwargs.get("temperature", 0.0),
                    system=system_prompt or "You are a helpful AI assistant.",
                    messages=messages,
                )

                return response.content[0].text

            except Exception as e:
                self.logger.error("claude_llm_failed", error=str(e), error_type=type(e).__name__)
                import traceback
                self.logger.error("claude_llm_traceback", trace=traceback.format_exc())
                return ""

        # Add required attributes for LightRAG compatibility
        claude_llm_func.__name__ = "claude_llm_func"
        claude_llm_func.max_async = 8
        claude_llm_func.max_token_size = 200000

        return claude_llm_func

    def _get_vision_function(self) -> Callable:
        """Get vision model function for processing images, charts, and tables.

        Returns:
            Async vision completion function
        """
        async def claude_vision_func(
            prompt: str,
            image_data: Any,
            **kwargs
        ) -> str:
            """Claude vision function for multimodal content."""
            try:
                from anthropic import AsyncAnthropic
                import base64

                client = AsyncAnthropic(api_key=self.config.anthropic_api_key)

                # Prepare multimodal content
                content = [{"type": "text", "text": prompt}]

                # Add image if provided
                if image_data:
                    if isinstance(image_data, bytes):
                        image_b64 = base64.b64encode(image_data).decode()
                    else:
                        image_b64 = image_data

                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_b64
                        }
                    })

                response = await client.messages.create(
                    model=self.config.claude_model,
                    max_tokens=kwargs.get("max_tokens", 2048),
                    messages=[{"role": "user", "content": content}],
                )

                return response.content[0].text

            except Exception as e:
                self.logger.error("vision_failed", error=str(e))
                return ""

        return claude_vision_func

    async def process_document(self, document_path: Path) -> Dict[str, Any]:
        """Process document using MinerU parser.

        This is the main ingestion function that:
        1. Parses PDF with MinerU (extracts text, tables, images, equations)
        2. Chunks the content
        3. Creates embeddings
        4. Stores in vector database
        5. Builds knowledge graph

        Args:
            document_path: Path to document (PDF, DOCX, etc.)

        Returns:
            Processing results including extracted content
        """
        if not self._initialized:
            return {
                "document": str(document_path),
                "status": "failed",
                "error": "RAG system not initialized"
            }

        self.logger.info(
            "processing_document",
            document=document_path.name,
            size_mb=round(document_path.stat().st_size / (1024 * 1024), 2),
        )

        try:
            # Process document through complete pipeline
            result = await self._rag.process_document_complete(
                file_path=str(document_path),
                output_dir=str(self.config.working_dir / "processed"),
                parse_method="auto"
            )

            # Check if result is None
            if result is None:
                self.logger.warning(
                    "document_processing_returned_none",
                    document=document_path.name
                )
                return {
                    "document": str(document_path),
                    "status": "success",
                    "message": "Document processed but no result data returned (may already exist)",
                    "result": {}
                }

            self.logger.info(
                "document_processed",
                document=document_path.name,
                status=result.get("status", "unknown") if isinstance(result, dict) else "success"
            )

            return {
                "document": str(document_path),
                "status": "success",
                "result": result if isinstance(result, dict) else {"status": "completed"},
            }

        except Exception as e:
            self.logger.error("document_processing_failed", document=document_path.name, error=str(e))
            return {
                "document": str(document_path),
                "status": "failed",
                "error": str(e),
            }

    # async def query(
    #     self,
    #     query_text: str,
    #     mode: str = "hybrid",
    #     top_k: Optional[int] = None,
    # ) -> Dict[str, Any]:
    #     """Query RAG system for relevant context.

    #     Args:
    #         query_text: User query
    #         mode: Query mode - "hybrid" (vector + graph), "local" (graph), "global" (summary), "naive" (vector only)
    #         top_k: Number of results to return

    #     Returns:
    #         Retrieved context with sources and scores
    #     """
    #     if not self._initialized:
    #         self.logger.warning("rag_not_initialized")
    #         return {
    #             "context": "RAG system not initialized.",
    #             "sources": [],
    #             "mode": "fallback"
    #         }

    #     self.logger.info("executing_query", mode=mode, query_length=len(query_text))

    #     try:
    #         # Ensure LightRAG is initialized
    #         if hasattr(self._rag, '_ensure_lightrag_initialized'):
    #             await self._rag._ensure_lightrag_initialized()

    #         # Query LightRAG directly (bypasses vision processing bug in RAG-Anything)
    #         lightrag = self._rag.lightrag

    #         if lightrag is None:
    #             raise RuntimeError("LightRAG not initialized")

    #         # Call LightRAG with proper parameters
    #         from lightrag.base import QueryParam
    #         query_param = QueryParam(
    #             mode=mode,
    #             only_need_context=False,
    #             stream=False,
    #         )

    #         result = await lightrag.aquery(query_text, param=query_param)

    #         print("👀👀👀👀👀👀👀👀👀👀👀👀👀👀") ######################################################################################### testing instruction
    #         print(result) ######################################################################################### testing instruction
    #         print("👀👀👀👀👀👀👀👀👀👀👀👀👀👀") ######################################################################################### testing instruction
            
    #         # Extract content from QueryResult
    #         if hasattr(result, 'content'):
    #             context = result.content

    #             # If content is None, consume the iterator
    #             if context is None and hasattr(result, 'response_iterator') and result.response_iterator:
    #                 chunks = []
    #                 async for chunk in result.response_iterator:
    #                     chunks.append(chunk)
    #                 context = ''.join(chunks)

    #         elif isinstance(result, str):
    #             context = result
    #         else:
    #             context = str(result)

    #         self.logger.info(
    #             "query_completed",
    #             context_length=len(context) if context else 0,
    #             mode=mode
    #         )

    #         return {
    #             "context": context or "",
    #             "sources": [],  # TODO: Extract from result.raw_data
    #             "mode": mode,
    #             "query": query_text
    #         }

    #     except Exception as e:
    #         self.logger.error("query_failed", error=str(e))
    #         return {
    #             "context": f"Query failed: {str(e)}",
    #             "sources": [],
    #             "mode": "error"
    #         }

    async def query(
        self,
        query_text: str,
        mode: str = "hybrid",
        top_k: Optional[int] = None,
        use_llm_enhancement: bool = False,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query RAG system for relevant context with optional LLM enhancement."""
        if not self._initialized:
            self.logger.warning("rag_not_initialized")
            return {
                "status": "error",
                "message": "RAG system not initialized",
                "data": {},
                "context": "",
                "sources": [],
                "mode": "fallback"
            }

        self.logger.info(
            "executing_query",
            mode=mode,
            query_length=len(query_text),
            use_llm_enhancement=use_llm_enhancement
        )

        try:
            # Ensure LightRAG is initialized
            if hasattr(self._rag, '_ensure_lightrag_initialized'):
                await self._rag._ensure_lightrag_initialized()

            lightrag = self._rag.lightrag
            if lightrag is None:
                raise RuntimeError("LightRAG not initialized")

            from lightrag.base import QueryParam
            
            if use_llm_enhancement:
                # FIRST: Get structured data with chunks
                data_param = QueryParam(
                    mode=mode,
                    only_need_context=True,
                    stream=False,
                    top_k=top_k if top_k else 60,
                )
                
                data_result = await lightrag.aquery_data(query_text, param=data_param)
                
                # Extract data
                if data_result and data_result.get("status") == "success":
                    data = data_result.get("data", {})
                    metadata = data_result.get("metadata", {})
                    chunks = data.get("chunks", [])
                else:
                    data = {}
                    metadata = {}
                    chunks = []
                
                entities = data.get("entities", [])
                relationships = data.get("relationships", [])
                references = data.get("references", [])
                
                # SECOND: Build explicit prompt with context
                context_str = "\n\n".join([
                    f"[Document: {chunk.get('file_path', 'Unknown')}]\n{chunk.get('content', '')}"
                    for chunk in chunks[:(top_k if top_k else 10)]
                ])
                
                # Create prompt with embedded context
                explicit_prompt = f"""Based ONLY on the following context from documents, answer the question.

                                    CONTEXT FROM DOCUMENTS:
                                    {context_str}

                                    QUESTION: {query_text}

                                    INSTRUCTIONS:
                                    - Answer using ONLY the information in the context above
                                    - If the answer is in the context, provide it directly with citations
                                    - The documents may reference future dates - report them as stated
                                    - If insufficient information, say "The provided documents do not contain enough information"
                                    - Do NOT mention knowledge cutoffs or refuse to answer about future dates
                                    """

                # THIRD: Get LLM response (NO system prompt needed)
                query_param = QueryParam(
                    mode=mode,
                    only_need_context=False,
                    stream=False,
                    top_k=top_k if top_k else 60,
                )
                
                llm_response_content = await lightrag.aquery(
                    explicit_prompt,
                    param=query_param,
                    system_prompt=None  # No system prompt needed
                )
                
                self.logger.info(
                    "llm_enhanced_query_completed",
                    response_length=len(llm_response_content) if llm_response_content else 0,
                    chunks_used=len(chunks)
                )
                
                # Build sources only (no raw chunks in response)
                sources = self._build_sources(references, chunks)
                
                # Return LLM-enhanced response WITHOUT raw chunks
                return {
                    "status": "success",
                    "message": "Query executed successfully with LLM enhancement",
                    "sources": sources,  # Only sources for citation
                    "mode": mode,
                    "query": query_text,
                    "llm_enhanced": True,
                    "llm_response": {
                        "content": llm_response_content if llm_response_content else "",
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "cost": 0.0
                    }
                }

            else:
                # Raw context retrieval - return chunks only
                query_param = QueryParam(
                    mode=mode,
                    only_need_context=True,
                    stream=False,
                    top_k=top_k if top_k else 60,
                )

                result = await lightrag.aquery_data(query_text, param=query_param)

                if result is None or result.get("status") != "success":
                    return {
                        "status": "failure",
                        "message": result.get("message", "Query failed") if result else "No results",
                        "data": {},
                        "context": "",
                        "sources": [],
                        "mode": mode,
                        "query": query_text
                    }

                data = result.get("data", {})
                metadata = result.get("metadata", {})
                entities = data.get("entities", [])
                relationships = data.get("relationships", [])
                chunks = data.get("chunks", [])
                references = data.get("references", [])

                context = self._build_context_from_data(entities, relationships, chunks, mode)
                sources = self._build_sources(references, chunks)

                # Return raw chunks when LLM enhancement is NOT used
                return {
                    "status": "success",
                    "message": result.get("message", "Query executed successfully"),
                    "data": data,  # Full structured data with chunks
                    "metadata": metadata,
                    "context": context,
                    "sources": sources,
                    "mode": mode,
                    "query": query_text,
                    "entities_count": len(entities),
                    "relationships_count": len(relationships),
                    "chunks_count": len(chunks),
                    "llm_enhanced": False
                }

        except Exception as e:
            self.logger.error("query_failed", error=str(e))
            import traceback
            self.logger.error("query_traceback", trace=traceback.format_exc())
            
            return {
                "status": "error",
                "message": f"Query failed: {str(e)}",
                "data": {},
                "context": "",
                "sources": [],
                "mode": "error",
                "query": query_text
            }

    def _build_context_from_data(
        self,
        entities: list,
        relationships: list,
        chunks: list,
        mode: str
    ) -> str:
        """Build human-readable context from structured data.
        
        Args:
            entities: List of entity objects
            relationships: List of relationship objects
            chunks: List of chunk objects
            mode: Query mode used
            
        Returns:
            Formatted context string
        """
        context_parts = []

        # Add chunks (most relevant content)
        if chunks:
            context_parts.append("=== RELEVANT CONTENT ===\n")
            for i, chunk in enumerate(chunks[:5], 1):  # Top 5 chunks
                content = chunk.get("content", "")
                file_path = chunk.get("file_path", "Unknown")
                context_parts.append(f"[Source {i}: {file_path}]")
                context_parts.append(content)
                context_parts.append("")  # Blank line

        # Add entities (if mode includes knowledge graph)
        if entities and mode in ["local", "global", "hybrid", "mix"]:
            context_parts.append("\n=== KEY ENTITIES ===")
            for entity in entities[:10]:  # Top 10 entities
                name = entity.get("entity_name", "")
                entity_type = entity.get("entity_type", "")
                description = entity.get("description", "")
                context_parts.append(f"• {name} ({entity_type}): {description}")

        # Add relationships (if mode includes knowledge graph)
        if relationships and mode in ["global", "hybrid", "mix"]:
            context_parts.append("\n=== KEY RELATIONSHIPS ===")
            for rel in relationships[:10]:  # Top 10 relationships
                src = rel.get("src_id", "")
                tgt = rel.get("tgt_id", "")
                description = rel.get("description", "")
                context_parts.append(f"• {src} → {tgt}: {description}")

        return "\n".join(context_parts) if context_parts else "No relevant information found."

    def _build_sources(self, references: list, chunks: list) -> list:
        """Build source references from data.
        
        Args:
            references: List of reference objects
            chunks: List of chunk objects
            
        Returns:
            List of source dictionaries
        """
        sources = []
        
        # Build from references
        for ref in references:
            sources.append({
                "reference_id": ref.get("reference_id", ""),
                "file_path": ref.get("file_path", ""),
                "type": "reference"
            })
        
        # Add chunk sources
        seen_paths = {ref.get("file_path") for ref in references}
        for chunk in chunks:
            file_path = chunk.get("file_path", "")
            if file_path and file_path not in seen_paths:
                sources.append({
                    "chunk_id": chunk.get("chunk_id", ""),
                    "file_path": file_path,
                    "type": "chunk"
                })
                seen_paths.add(file_path)
        
        return sources

    async def query_multimodal(
        self,
        query_text: str,
        multimodal_content: List[Dict[str, Any]],
        mode: str = "hybrid"
    ) -> Dict[str, Any]:
        """Query with multimodal content (images, equations, tables).

        Args:
            query_text: User query
            multimodal_content: List of multimodal items (images, tables, etc.)
            mode: Query mode

        Returns:
            Retrieved context with multimodal understanding
        """
        if not self._initialized:
            return await self.query(query_text, mode)

        try:
            result = await self._rag.aquery_with_multimodal(
                query_text,
                multimodal_content=multimodal_content,
                mode=mode
            )

            context = result if isinstance(result, str) else str(result)

            return {
                "context": context,
                "sources": [],
                "mode": f"{mode}_multimodal",
                "query": query_text
            }

        except Exception as e:
            self.logger.error("multimodal_query_failed", error=str(e))
            return await self.query(query_text, mode)

    async def health_check(self) -> bool:
        """Check RAG system health.

        Returns:
            True if system is healthy
        """
        if not self._initialized:
            return False

        try:
            return self.config.working_dir.exists()
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "initialized": self._initialized,
            "working_dir": str(self.config.working_dir),
            "embedding_model": self.config.embedding_model,
            "parser": "mineru",
            "multimodal_enabled": True,
        }