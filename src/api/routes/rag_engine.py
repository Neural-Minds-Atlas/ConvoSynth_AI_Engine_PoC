"""API routes for RAG Engine Agent."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
import structlog

from src.db.mongodb import get_collection
from src.db.models import RAGEngineOutput
from src.agents.rag_engine.agent import RAGEngineAgent
from src.agents.base import AgentRequest

logger = structlog.get_logger(__name__)

router = APIRouter()

# Request/Response Models
class RAGEngineRequest(BaseModel):
    """Request model for RAG retrieval."""
    session_id: str = Field(..., alias="sessionId")
    user_id: str = Field(..., alias="userId")
    query: str
    documents: List[str] = Field(default_factory=list)
    rag_mode: str = Field(default="hybrid", alias="ragMode")  # hybrid, naive, local, global

    class Config:
        populate_by_name = True


class RAGEngineResponse(BaseModel):
    """Response model for RAG retrieval."""
    success: bool
    session_id: str = Field(..., alias="sessionId")
    retrieved_context: str = Field(..., alias="retrievedContext")
    source_documents: List[str] = Field(..., alias="sourceDocuments")
    key_findings: List[str] = Field(..., alias="keyFindings")
    confidence_score: float = Field(..., alias="confidenceScore")
    total_chunks: int = Field(..., alias="totalChunks")
    execution_time: float = Field(..., alias="executionTime")
    timestamp: str
    error: Optional[str] = None

    class Config:
        populate_by_name = True


@router.post("/rag-engine/retrieve", response_model=RAGEngineResponse, tags=["agents"])
async def retrieve_context(
    request: RAGEngineRequest = Body(...)
):
    """
    Retrieve context from RAG system.

    Uses intelligent RAG modes to retrieve relevant context from documents.
    """
    try:
        logger.info("rag_engine_request_received", session_id=request.session_id, mode=request.rag_mode)

        # Initialize RAG Engine Agent
        agent = RAGEngineAgent()

        # Create agent request
        agent_request = AgentRequest(
            user_input=request.query,
            context={
                "documents": request.documents,
                "rag_mode": request.rag_mode
            },
            session_id=request.session_id
        )

        # Execute agent
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error("rag_engine_failed", errors=response.errors)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "RAG retrieval failed",
                    "errors": response.errors
                }
            )

        output = response.output

        # Save RAG Engine output to MongoDB
        try:
            rag_collection = get_collection("rag_engine_outputs")

            # Create RAG Engine Output document
            rag_output = RAGEngineOutput(
                retrievedContext=output.get("retrieved_context", ""),
                sourceDocuments=output.get("source_documents", []),
                chunkSummaries=output.get("chunk_summaries", []),
                keyFindings=output.get("key_findings", []),
                confidenceScore=output.get("confidence_score", 0.0),
                totalChunksRetrieved=output.get("total_chunks", 0),
                ragMode=request.rag_mode
            )

            # Save to MongoDB
            await rag_collection.insert_one(
                rag_output.model_dump(by_alias=True, exclude_none=False)
            )
            logger.info("rag_engine_output_saved_to_mongodb", session_id=request.session_id)

        except Exception as db_error:
            logger.error(
                "rag_engine_mongodb_save_failed",
                session_id=request.session_id,
                error=str(db_error),
                error_type=type(db_error).__name__
            )
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {str(db_error)}")

        logger.info("rag_engine_completed", session_id=request.session_id, chunks=output.get("total_chunks"))

        return RAGEngineResponse(
            success=True,
            session_id=request.session_id,
            retrieved_context=output.get("retrieved_context", ""),
            source_documents=output.get("source_documents", []),
            key_findings=output.get("key_findings", []),
            confidence_score=output.get("confidence_score", 0.0),
            total_chunks=output.get("total_chunks", 0),
            execution_time=response.metadata.get("execution_time", 0.0),
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("rag_engine_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
