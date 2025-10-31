"""API route for Query Agent - RAG retrieval and context enhancement."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from datetime import datetime
import structlog

from src.agents.query import QueryAgent
from src.agents.base import AgentRequest
from src.db.mongodb import get_collection
from src.db.models import QueryAgentOutput, GeneratedQuery, RetrievedContext

logger = structlog.get_logger(__name__)

router = APIRouter()

# In-memory agent storage (replace with proper state management in production)
query_agents: Dict[str, QueryAgent] = {}


# Request Models
class DataRequirements(BaseModel):
    """Data requirements from Conversation Agent."""
    documents_requested: List[str] = Field(default_factory=list, alias="documentsRequested")
    content_to_extract: List[str] = Field(default_factory=list, alias="contentToExtract")
    metrics: List[str] = Field(default_factory=list)
    time_periods: List[str] = Field(default_factory=list, alias="timePeriods")
    comparisons: List[str] = Field(default_factory=list)
    data_categories: List[str] = Field(default_factory=list, alias="dataCategories")

    class Config:
        populate_by_name = True


class QueryAgentRequest(BaseModel):
    """Request model for Query Agent."""
    session_id: Optional[str] = Field(default=None, description="Session ID for tracking", alias="sessionId")
    data_requirements: DataRequirements = Field(
        ...,
        description="Data requirements from Conversation Agent",
        alias="dataRequirements"
    )
    rag_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional RAG configuration overrides (e.g., rag_endpoint)",
        alias="ragConfig"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "sessionId": "session_789",
                "dataRequirements": {
                    "documentsRequested": ["Stock History Becton, Dickinson and Company (BDX) Stock Historical Prices & Data - Yahoo Finance.pdf"],
                    "contentToExtract": [
                        "historical prices",
                        "",
                        ""
                    ],
                    "metrics": ["open", "high", "low", "close"],
                    "timePeriods": ["Sep 2025", "Aug 2025"],
                    "comparisons": ["Sep vs Aug"],
                    "dataCategories": ["financial"]
                },
                "ragConfig": {
                    "rag_endpoint": "http://localhost:8000/api/v1/query"
                },
                "context": {}
            }
        }


# Response Models
class QueryInfo(BaseModel):
    """Information about a generated query."""
    query: str
    query_type: str = Field(..., alias="queryType")
    priority: str
    filters: Dict[str, Any]
    rationale: str

    class Config:
        populate_by_name = True


class RetrievedChunk(BaseModel):
    """Retrieved chunk information."""
    chunk_id: str = Field(..., alias="chunkId")
    content: str
    document_name: str = Field(..., alias="documentName")
    relevance_score: float = Field(..., alias="relevanceScore")
    metadata: Dict[str, Any]
    token_count: int = Field(..., alias="tokenCount")

    class Config:
        populate_by_name = True


class SynthesizedAnswer(BaseModel):
    """Synthesized answer for a theme."""
    answer: str
    key_points: List[str] = Field(..., alias="keyPoints")
    metrics: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    confidence: str
    gaps: List[str]

    class Config:
        populate_by_name = True


class PerformanceMetrics(BaseModel):
    """Performance metrics for Query Agent execution."""
    query_generation_time: float = Field(..., alias="queryGenerationTime")
    retrieval_time: float = Field(..., alias="retrievalTime")
    synthesis_time: float = Field(..., alias="synthesisTime")
    total_tokens_retrieved: int = Field(..., alias="totalTokensRetrieved")
    total_queries_generated: int = Field(..., alias="totalQueriesGenerated")

    class Config:
        populate_by_name = True


class QueryAgentResponse(BaseModel):
    """Response model for Query Agent."""
    success: bool
    session_id: Optional[str] = Field(default=None, alias="sessionId")
    response: str
    generated_queries: List[Dict[str, Any]] = Field(default_factory=list, alias="generatedQueries")
    synthesized_context: Dict[str, Any] = Field(default_factory=dict, alias="synthesizedContext")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, alias="performanceMetrics")
    tool_calls_made: int = Field(default=0, alias="toolCallsMade")
    timestamp: str
    error: Optional[str] = None

    class Config:
        populate_by_name = True


# Endpoints

@router.post("/query-agent", response_model=QueryAgentResponse, tags=["agents"])
async def query_agent_endpoint(
    query_request: QueryAgentRequest = Body(...)
):
    """
    Query Agent endpoint - RAG retrieval and context enhancement.

    This agent processes data requirements from the Conversation Agent and:
    1. Generates targeted queries based on data requirements
    2. Retrieves relevant context from RAG engine using intelligent mode selection
    3. Synthesizes retrieved chunks into coherent answers
    4. Maintains inter-query context for token efficiency

    **Workflow:**
    1. Receives data requirements from Conversation Agent
    2. Analyzes data requirements (documents, metrics, comparisons, time periods)
    3. Generates 5-10 targeted queries with appropriate filters
    4. Retrieves context for each query from RAG engine
    5. Intelligently selects RAG mode (hybrid/naive/local/global) per query
    6. Synthesizes all contexts into organized answers
    7. Returns enhanced context for downstream agents

    **Performance Targets:**
    - Response Time: <2 seconds
    - Accuracy: 98% intent capture
    - Context Relevance: 95% minimum

    **Input Requirements:**
    - dataRequirements (required): Contains:
        - documentsRequested: List of document names to search
        - contentToExtract: Specific content/topics to extract
        - metrics: KPIs and metrics to retrieve
        - timePeriods: Time ranges for filtering
        - comparisons: Comparison types (e.g., "Q2 vs Q3")
        - dataCategories: Categories like "operational", "financial", etc.
    - ragConfig (optional): RAG configuration overrides (e.g., custom rag_endpoint)
    - sessionId (optional): For session tracking and reuse
    - context (optional): Additional context data
    """
    try:
        # Generate session ID if not provided
        session_id = query_request.session_id
        if not session_id:
            import uuid
            session_id = f"query_{uuid.uuid4().hex[:12]}"
            logger.info("new_query_session_created", session_id=session_id)

        # Get or create Query Agent
        if session_id not in query_agents:
            logger.info("initializing_query_agent", session_id=session_id)
            
            # Get RAG endpoint from config
            rag_endpoint = query_request.rag_config.get("rag_endpoint")
            agent = QueryAgent(rag_endpoint=rag_endpoint)
            query_agents[session_id] = agent
        else:
            agent = query_agents[session_id]
            logger.info("reusing_existing_query_agent", session_id=session_id)

        # Create agent request with only data requirements
        agent_request = AgentRequest(
            user_input="Process data requirements and retrieve context",
            context={
                "dataRequirements": query_request.data_requirements.model_dump(by_alias=True),
                "ragConfig": query_request.rag_config,
                **query_request.context
            },
            session_id=session_id
        )

        # Execute agent
        logger.info("query_agent_execution_started", session_id=session_id)
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error(
                "query_agent_execution_failed",
                session_id=session_id,
                errors=response.errors
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Query agent execution failed",
                    "errors": response.errors,
                    "session_id": session_id
                }
            )

        output = response.output

        logger.info(
            "query_agent_execution_completed",
            session_id=session_id,
            queries_generated=len(output.get("generated_queries", [])),
            contexts_retrieved=len(output.get("retrieved_contexts", [])),
            tool_calls=output.get("tool_calls_made", 0)
        )

        # Save Query Agent output to MongoDB
        try:
            query_agent_collection = get_collection("query_agent_outputs")

            # Convert generated queries to model format
            generated_queries = []
            for idx, query_data in enumerate(output.get("generated_queries", [])):
                # Generate query ID if not present
                query_id = query_data.get("query_id", f"query_{session_id}_{idx}")

                # Convert priority to int (handle "high", "medium", "low" strings)
                priority_value = query_data.get("priority", 3)
                if isinstance(priority_value, str):
                    priority_map = {"high": 5, "medium": 3, "low": 1}
                    priority_value = priority_map.get(priority_value.lower(), 3)
                elif not isinstance(priority_value, int):
                    priority_value = 3

                generated_queries.append(GeneratedQuery(
                    queryId=query_id,
                    queryText=query_data.get("query", ""),
                    queryType=query_data.get("query_type", "topic"),
                    ragMode=query_data.get("rag_mode", "hybrid"),
                    priority=int(priority_value),
                    metadata=query_data.get("filters", {})
                ))

            # Convert retrieved contexts to model format
            retrieved_contexts = []
            for context_data in output.get("retrieved_contexts", []):
                # Extract document sources from chunks
                chunks = context_data.get("chunks", [])
                document_sources = list(set([
                    chunk.get("document_name", "unknown")
                    for chunk in chunks
                    if isinstance(chunk, dict)
                ]))

                # Calculate total token count from chunks
                token_count = sum([
                    chunk.get("token_count", 0)
                    for chunk in chunks
                    if isinstance(chunk, dict)
                ])

                retrieved_contexts.append(RetrievedContext(
                    queryId=context_data.get("query_id", ""),
                    documentSources=document_sources,
                    retrievedChunks=chunks,
                    relevanceScore=context_data.get("relevance_score", 0.0),
                    tokenCount=token_count,
                    ragMode=context_data.get("rag_mode", "hybrid")
                ))

            # Create Query Agent Output document
            query_agent_output = QueryAgentOutput(
                sessionId=session_id,
                generatedQueries=generated_queries,
                retrievedContexts=retrieved_contexts,
                synthesizedContext=output.get("synthesized_context", {}),
                keyFindings=output.get("key_findings", []),
                totalTokensRetrieved=output.get("performance_metrics", {}).get("total_tokens_retrieved", 0),
                presentationMetadata=output.get("presentation_metadata", {}),
                createdAt=datetime.utcnow()
            )

            # Save to MongoDB
            await query_agent_collection.insert_one(
                query_agent_output.model_dump(by_alias=True, exclude_none=False)
            )
            logger.info("query_agent_output_saved_to_mongodb", session_id=session_id)

        except Exception as db_error:
            logger.error(
                "query_agent_mongodb_save_failed",
                session_id=session_id,
                error=str(db_error),
                error_type=type(db_error).__name__
            )
            # Raise error to see what's wrong
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {str(db_error)}")

        return QueryAgentResponse(
            success=True,
            session_id=session_id,
            response=output.get("response", ""),
            generated_queries=output.get("generated_queries", []),
            synthesized_context=output.get("synthesized_context", {}),
            performance_metrics=output.get("performance_metrics", {}),
            tool_calls_made=output.get("tool_calls_made", 0),
            timestamp=output.get("timestamp", "")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "query_agent_endpoint_error",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query-agent/reset", tags=["agents"])
async def reset_query_agent(session_id: str = Body(..., embed=True)):
    """
    Reset Query Agent state for a session.

    Clears all generated queries, retrieved contexts, and synthesized data.
    """
    try:
        if session_id in query_agents:
            agent = query_agents[session_id]
            agent.reset()
            logger.info("query_agent_reset", session_id=session_id)

            return {
                "message": "Query Agent reset successfully",
                "sessionId": session_id
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Query Agent session {session_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("reset_query_agent_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query-agent/session/{session_id}", tags=["agents"])
async def get_query_agent_session(session_id: str):
    """
    Get Query Agent session information.

    Returns current state including generated queries and performance metrics.
    """
    try:
        if session_id not in query_agents:
            return {
                "sessionId": session_id,
                "exists": False,
                "message": "Session not found"
            }

        agent = query_agents[session_id]

        return {
            "sessionId": session_id,
            "exists": True,
            "generatedQueries": len(agent.generated_queries),
            "retrievedContexts": len(agent.retrieved_contexts),
            "hasSynthesizedContext": bool(agent.synthesized_context),
            "performanceMetrics": agent.performance_metrics,
            "toolCallsMade": agent.tool_call_count
        }

    except Exception as e:
        logger.error("get_query_agent_session_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/query-agent/session/{session_id}", tags=["agents"])
async def delete_query_agent_session(session_id: str):
    """
    Delete Query Agent session.

    Removes the agent from memory.
    """
    try:
        if session_id in query_agents:
            del query_agents[session_id]
            logger.info("query_agent_session_deleted", session_id=session_id)

            return {
                "message": "Query Agent session deleted successfully",
                "sessionId": session_id
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Query Agent session {session_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_query_agent_session_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query-agent/sessions", tags=["agents"])
async def list_query_agent_sessions():
    """
    List all active Query Agent sessions.

    Returns session IDs with their current state.
    """
    try:
        sessions = []
        for session_id, agent in query_agents.items():
            sessions.append({
                "sessionId": session_id,
                "generatedQueries": len(agent.generated_queries),
                "retrievedContexts": len(agent.retrieved_contexts),
                "hasSynthesizedContext": bool(agent.synthesized_context),
                "toolCallsMade": agent.tool_call_count
            })

        return {
            "totalSessions": len(sessions),
            "sessions": sessions
        }

    except Exception as e:
        logger.error("list_query_agent_sessions_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))