# ============================================================================
# File: api/routes/chat.py
# ============================================================================
"""Chat/conversation endpoints for RAG queries."""

from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
import structlog

from src.api.dependencies import get_rag_client
from src.rag_anything.client import RAGAnythingClient
from src.rag_anything.retrieval import QueryProcessor

logger = structlog.get_logger(__name__)

router = APIRouter()


class ContextChunk(BaseModel):
    """Single context chunk from retrieval."""
    content: str = Field(..., description="Chunk text content")
    file_path: Optional[str] = Field(None, description="Source file path")
    chunk_id: Optional[str] = Field(None, description="Unique chunk identifier")
    reference_id: Optional[str] = Field(None, description="Reference ID for citations")


class LLMResponse(BaseModel):
    """LLM-enhanced response (only present if use_llm_enhancement=True)."""
    content: str = Field(..., description="LLM-generated response text")
    prompt_tokens: int = Field(0, description="Number of tokens in prompt")
    completion_tokens: int = Field(0, description="Number of tokens in completion")
    cost: float = Field(0.0, description="Estimated API cost")


class ChatRequest(BaseModel):
    """Chat request with query."""
    query: str = Field(..., description="User query", min_length=1, max_length=1000)
    mode: Optional[str] = Field(
        default="hybrid",
        description="Retrieval mode: hybrid, naive, local, global, mix"
    )
    top_k: Optional[int] = Field(
        default=5, 
        ge=1, 
        le=100, 
        description="Number of context chunks to retrieve"
    )
    use_llm_enhancement: Optional[bool] = Field(
        default=False,
        description="If True, use LLM to generate enhanced response from retrieved context"
    )
    system_prompt: Optional[str] = Field(
        default="You are a helpful AI assistant that answers questions based STRICTLY on the provided context.",
        description="Custom system prompt for LLM enhancement (only used if use_llm_enhancement=True)"
    )


class ChatResponse(BaseModel):
    """Simplified chat response optimized for agent workflow."""
    
    # Query info
    status: str = Field(..., description="Query execution status: success, failure, error")
    message: str = Field(..., description="Human-readable status message")
    query: str = Field(..., description="Original user query")
    mode: str = Field(..., description="Retrieval mode used")
    
    # Context - LIST OF CHUNKS instead of concatenated string
    context: List[ContextChunk] = Field(
        default_factory=list,
        description="List of relevant context chunks (preserves individual chunks for agent processing)"
    )
    context_length: int = Field(..., description="Total character count across all chunks")
    
    # Sources for citation
    sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Source file references"
    )
    
    # Query understanding metadata
    query_intent: Optional[str] = Field(
        None,
        description="Detected query intent: factual, comparison, trend_analysis, summarization"
    )
    metric_type: Optional[str] = Field(
        None,
        description="Detected financial metric: revenue, earnings, ebitda, margin, growth, general"
    )
    
    # LLM Enhancement (only present if requested)
    llm_enhanced: bool = Field(
        default=False,
        description="Whether LLM enhancement was used"
    )
    llm_response: Optional[LLMResponse] = Field(
        None,
        description="LLM-generated enhanced response (only if use_llm_enhancement=True)"
    )


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    req: ChatRequest,
    rag_client: RAGAnythingClient = Depends(get_rag_client)
):
    """Query RAG system with conversational interface.
    
    Supports two modes:
    1. Raw context retrieval (default): Returns structured chunks for agent processing
    2. LLM-enhanced retrieval: Uses LLM to generate coherent response from context
    
    Context is returned as a list of individual chunks rather than concatenated text,
    preserving chunk boundaries and relevance for multi-query workflows.
    
    Args:
        req: Chat request with query and optional LLM enhancement
        rag_client: RAG client instance
        
    Returns:
        Simplified chat response with chunk-based context (limited to top_k chunks)
        If use_llm_enhancement=True, includes LLM-generated response
        
    Raises:
        HTTPException: If RAG not initialized or query fails
    """
    if not rag_client or not rag_client._initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized"
        )
    
    logger.info(
        "chat_query_received",
        query_length=len(req.query),
        mode=req.mode,
        top_k=req.top_k,
        use_llm_enhancement=req.use_llm_enhancement
    )
    
    try:
        # Process query to extract intent and entities
        query_processor = QueryProcessor()
        processed_query = query_processor.process_query(req.query)
        
        query_intent = processed_query.get("intent")
        metric_type = processed_query.get("metric_type")
        
        logger.info(
            "query_processed",
            intent=query_intent,
            metric_type=metric_type
        )
        
        # Retrieve context from RAG (with or without LLM enhancement)
        result = await rag_client.query(
            query_text=req.query,
            mode=req.mode,
            top_k=req.top_k,
            use_llm_enhancement=req.use_llm_enhancement,
            system_prompt=req.system_prompt
        )
        
        # Check if query was successful
        if result.get("status") != "success":
            logger.warning("query_failed", message=result.get("message"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Query failed")
            )
        
        # Extract chunks from result data
        raw_data = result.get("data", {})
        chunks_data = raw_data.get("chunks", [])
        
        # LIMIT TO TOP_K CHUNKS
        chunks_data = chunks_data[:req.top_k]
        
        # Convert to ContextChunk objects
        context_chunks = [
            ContextChunk(
                content=chunk.get("content", ""),
                file_path=chunk.get("file_path"),
                chunk_id=chunk.get("chunk_id"),
                reference_id=chunk.get("reference_id")
            )
            for chunk in chunks_data
        ]
        
        # Calculate total context length
        total_length = sum(len(chunk.content) for chunk in context_chunks)
        
        # Get sources
        sources = result.get("sources", [])
        
        # Extract LLM response if enhancement was used
        llm_enhanced = result.get("llm_enhanced", False)
        llm_response = None
        
        if llm_enhanced and "llm_response" in result:
            llm_data = result.get("llm_response", {})
            llm_response = LLMResponse(
                content=llm_data.get("content", ""),
                prompt_tokens=llm_data.get("prompt_tokens", 0),
                completion_tokens=llm_data.get("completion_tokens", 0),
                cost=llm_data.get("cost", 0.0)
            )
        
        logger.info(
            "chat_query_completed",
            chunks_count=len(context_chunks),
            requested_top_k=req.top_k,
            total_context_length=total_length,
            llm_enhanced=llm_enhanced
        )
        
        # Build simplified response
        return ChatResponse(
            status=result.get("status", "success"),
            message=result.get("message", "Query executed successfully"),
            query=req.query,
            mode=req.mode,
            context=context_chunks,  # List of chunks, limited to top_k
            context_length=total_length,
            sources=sources,
            query_intent=query_intent,
            metric_type=metric_type,
            llm_enhanced=llm_enhanced,
            llm_response=llm_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("chat_query_failed", error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat query failed: {str(e)}"
        )