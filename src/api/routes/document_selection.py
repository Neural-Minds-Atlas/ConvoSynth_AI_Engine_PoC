"""API routes for Document Selection Agent."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from datetime import datetime
import structlog

from src.agents.document_selection import DocumentSelectionAgent
from src.agents.base import AgentRequest
from src.db.mongodb import get_collection
from src.db.models import DocumentSelectionOutput, SelectedDocument as SelectedDocumentModel

logger = structlog.get_logger(__name__)

router = APIRouter()


# Request/Response Models
class DocumentSelectionRequest(BaseModel):
    """Request model for document selection."""
    presentation_requirements: Dict[str, Any] = Field(
        ...,
        description="Presentation requirements from conversation agent",
        alias="presentationRequirements"
    )
    data_requirements: Dict[str, Any] = Field(
        ...,
        description="Data requirements from conversation agent",
        alias="dataRequirements"
    )
    visual_preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Visual preferences",
        alias="visualPreferences"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        default=None,
        description="User profile for RBAC",
        alias="userProfile"
    )
    accessible_documents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="User's accessible documents",
        alias="accessibleDocuments"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "presentationRequirements": {
                    "topic": "Q4 2024 Financial Performance",
                    "key_themes": ["revenue", "profit", "expenses"],
                    "target_audience": "Board of Directors",
                    "num_slides": 10,
                    "tone": "professional"
                },
                "dataRequirements": {
                    "content_to_extract": ["revenue figures", "expense breakdown"],
                    "specific_metrics": ["Q4 revenue", "operating expenses"]
                },
                "visualPreferences": {
                    "chart_types": ["bar", "line"],
                    "style": "professional"
                },
                "userProfile": {
                    "userId": "user123",
                    "name": "Test User",
                    "role": "CFO",
                    "department": "Finance"
                },
                "accessibleDocuments": []
            }
        }


class SelectedDocument(BaseModel):
    """Model for a selected document."""
    document_id: str = Field(..., alias="documentId")
    document_name: str = Field(..., alias="documentName")
    doc_type: str = Field(..., alias="docType")
    department: str
    topics: List[str] = Field(default_factory=list)
    summary: str
    relevance_score: Optional[float] = Field(default=None, alias="relevanceScore")
    match_reasons: Optional[List[str]] = Field(default_factory=list, alias="matchReasons")

    class Config:
        populate_by_name = True


class DocumentSelectionResponse(BaseModel):
    """Response model for document selection."""
    selected_documents: List[SelectedDocument] = Field(..., alias="selectedDocuments")
    total_selected: int = Field(..., alias="totalSelected")
    metadata_queries_made: int = Field(..., alias="metadataQueriesMade")
    candidate_documents_found: int = Field(..., alias="candidateDocumentsFound")
    tool_calls_made: int = Field(..., alias="toolCallsMade")
    next_action: str = Field(..., alias="nextAction")
    handoff_to_agent: str = Field(..., alias="handoffToAgent")
    execution_time: float = Field(..., alias="executionTime")
    timestamp: str

    class Config:
        populate_by_name = True


@router.post("/select-documents", response_model=DocumentSelectionResponse, tags=["document-selection"])
async def select_documents(
    request: DocumentSelectionRequest = Body(...)
):
    """
    Select relevant documents based on presentation requirements using metadata RAG.

    This endpoint:
    1. Analyzes data requirements from conversation agent
    2. Queries document metadata corpus
    3. Scores and ranks documents by relevance
    4. Returns top 5-10 most relevant documents

    **Algorithm:**
    - Uses Cohere LLM with Zero-shot ReAct pattern
    - Metadata RAG tool with hardcoded document corpus
    - Intelligent scoring based on topics, departments, doc types
    - Fallback mechanism for reliability

    **Performance:**
    - Target: <3 seconds
    - Accuracy: 95% relevance

    **Output:**
    - List of selected documents with relevance scores
    - Handoff to RAG Engine for detailed content retrieval
    """
    try:
        logger.info(
            "document_selection_request_received",
            topic=request.presentation_requirements.get("topic"),
            themes_count=len(request.presentation_requirements.get("key_themes", [])),
            user_id=request.user_profile.get("userId") if request.user_profile else None
        )

        # Initialize Document Selection Agent
        agent = DocumentSelectionAgent()

        # Create agent request
        agent_request = AgentRequest(
            user_input=f"Select documents for: {request.presentation_requirements.get('topic', 'Unknown topic')}",
            context={
                "extracted_information": {
                    "presentation_requirements": request.presentation_requirements,
                    "data_requirements": request.data_requirements,
                    "visual_preferences": request.visual_preferences
                },
                "user_profile": request.user_profile or {},
                "accessible_documents": request.accessible_documents,
                "rbac_validation": {}
            }
        )

        # Execute agent
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error(
                "document_selection_failed",
                errors=response.errors
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Document selection failed",
                    "errors": response.errors
                }
            )

        output = response.output

        # Transform selected documents to response model
        selected_docs = []
        for doc in output.get("selected_documents", []):
            selected_docs.append(SelectedDocument(
                document_id=doc.get("document_id", ""),
                document_name=doc.get("document_name", ""),
                doc_type=doc.get("doc_type", ""),
                department=doc.get("department", ""),
                topics=doc.get("topics", []),
                summary=doc.get("summary", ""),
                relevance_score=doc.get("relevance_score"),
                match_reasons=doc.get("match_reasons", [])
            ))

        logger.info(
            "document_selection_completed",
            total_selected=len(selected_docs),
            execution_time=response.metadata.get("execution_time"),
            tool_calls=output.get("tool_calls_made", 0)
        )

        # Save Document Selection output to MongoDB
        try:
            doc_selection_collection = get_collection("document_selections")

            # Convert selected documents to model format
            selected_docs_models = []
            for doc in output.get("selected_documents", []):
                # Join match_reasons into a single string for selectionReason
                match_reasons = doc.get("match_reasons", [])
                selection_reason = "; ".join(match_reasons) if match_reasons else "Selected based on relevance"

                selected_docs_models.append(SelectedDocumentModel(
                    documentId=doc.get("document_id", ""),
                    documentName=doc.get("document_name", ""),
                    documentType=doc.get("doc_type", "unknown"),  # Fixed: was docType
                    keyTopics=doc.get("topics", []),  # Fixed: was topics
                    relevanceScore=doc.get("relevance_score", 0.0),
                    selectionReason=selection_reason  # Fixed: was matchReasons (list)
                ))

            # Create Document Selection Output
            doc_selection_output = DocumentSelectionOutput(
                selectedDocuments=selected_docs_models,
                totalDocumentsEvaluated=output.get("candidate_documents_found", 0),
                selectionCriteria=[
                    f"Relevance threshold",
                    f"Topic matching",
                    f"Total selected: {output.get('total_selected', 0)}"
                ],
                rejectedDocuments=[]
            )

            # Save to MongoDB
            await doc_selection_collection.insert_one(
                doc_selection_output.model_dump(by_alias=True, exclude_none=False)
            )
            logger.info("document_selection_saved_to_mongodb", total_selected=len(selected_docs_models))

        except Exception as db_error:
            logger.error(
                "document_selection_mongodb_save_failed",
                error=str(db_error),
                error_type=type(db_error).__name__
            )
            # Raise error to see what's wrong
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {str(db_error)}")

        return DocumentSelectionResponse(
            selected_documents=selected_docs,
            total_selected=output.get("total_selected", 0),
            metadata_queries_made=output.get("metadata_queries_made", 0),
            candidate_documents_found=output.get("candidate_documents_found", 0),
            tool_calls_made=output.get("tool_calls_made", 0),
            next_action=output.get("next_action", "handoff_to_rag_engine"),
            handoff_to_agent=output.get("handoff_to_agent", "RAG Engine"),
            execution_time=response.metadata.get("execution_time", 0.0),
            timestamp=output.get("timestamp", "")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "document_selection_endpoint_error",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata/corpus", tags=["document-selection"])
async def get_metadata_corpus():
    """
    Get the current document metadata corpus.

    Returns all available documents in the metadata corpus with their metadata.
    Useful for understanding what documents are available for selection.
    """
    try:
        agent = DocumentSelectionAgent()

        documents = [
            {
                "documentId": doc["document_id"],
                "documentName": doc["document_name"],
                "docType": doc["doc_type"],
                "department": doc["department"],
                "topics": doc["topics"],
                "tags": doc["tags"],
                "summary": doc["summary"],
                "dateRange": doc["date_range"],
                "sizeMb": doc.get("size_mb"),
                "pageCount": doc.get("page_count"),
                "createdAt": doc.get("created_at"),
                "accessLevel": doc.get("access_level")
            }
            for doc in agent.metadata_tool.document_corpus
        ]

        return {
            "totalDocuments": len(documents),
            "documents": documents,
            "message": "These are hardcoded/dummy documents for testing. In production, this would query a real document database."
        }

    except Exception as e:
        logger.error("get_corpus_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata/search", tags=["document-selection"])
async def search_metadata(
    topics: Optional[str] = None,
    department: Optional[str] = None,
    doc_type: Optional[str] = None
):
    """
    Search the metadata corpus by topics, department, or document type.

    Query parameters:
    - topics: Comma-separated list of topics (e.g., "revenue,profit")
    - department: Department name (e.g., "Finance")
    - doc_type: Document type (e.g., "financial_report")
    """
    try:
        agent = DocumentSelectionAgent()

        # Parse topics
        topic_list = [t.strip() for t in topics.split(",")] if topics else []

        # Build query parameters
        query_params = {}
        if topic_list:
            query_params["key_topics"] = topic_list
        if department:
            query_params["departments"] = [department]
        if doc_type:
            query_params["document_types"] = [doc_type]

        if not query_params:
            return {
                "message": "Please provide at least one search parameter",
                "totalFound": 0,
                "documents": []
            }

        # Query metadata
        import json
        results = agent.metadata_tool.query_metadata(query_params)
        results_dict = json.loads(results)

        return {
            "message": "Search completed",
            "totalFound": results_dict.get("total_found", 0),
            "returned": results_dict.get("returned", 0),
            "documents": results_dict.get("documents", []),
            "queryParameters": query_params
        }

    except Exception as e:
        logger.error("metadata_search_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
