"""
FastAPI routes for Edit Request Classification Agent
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import time

from src.agents.edit_request_classifier.agent import (
    EditRequestClassifierAgent,
    EditClassificationResult
)
from src.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/edit-request-classifier",
    tags=["Edit Request Classifier Agent"]
)

# Initialize agent (singleton pattern)
classifier_agent: Optional[EditRequestClassifierAgent] = None


def get_classifier_agent() -> EditRequestClassifierAgent:
    """Get or create classifier agent instance"""
    global classifier_agent
    if classifier_agent is None:
        classifier_agent = EditRequestClassifierAgent()
    return classifier_agent


# ============================================================================
# Request/Response Models
# ============================================================================

class EditClassificationRequest(BaseModel):
    """Request model for edit classification"""
    user_request: str = Field(
        ..., 
        description="Raw user edit request",
        min_length=1,
        example="Make the title of slide 2 bigger and change it to blue"
    )
    id: str = Field(
        ...,
        description="Unique identifier for this request",
        example="req_abc123"
    )
    session_id: str = Field(
        ..., 
        description="Session identifier",
        example="sess_abc123xyz"
    )
    presentation_id: str = Field(
        ..., 
        description="Presentation identifier",
        example="pres_xyz789abc"
    )
    user_id: str = Field(
        ..., 
        description="User identifier",
        example="user_123456"
    )


class EditClassificationResponse(BaseModel):
    """Response model for edit classification"""
    success: bool = Field(..., description="Whether classification was successful")
    id: str = Field(..., description="Request identifier (mirrors input id)")
    presentation_id: str = Field(..., description="Presentation identifier")
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    edit_request_class: str = Field(
        ..., 
        description="Classification category",
        example="visual_edit"
    )
    modified_user_request: str = Field(
        ..., 
        description="Structured prompt with exact changes",
        example="Increase the font size of the title on slide 2 to 36px and change the color to #0066CC (blue)"
    )
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    response: str = Field(default="", description="Additional information or human-readable response")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    agent: str
    timestamp: float


# ============================================================================
# Routes
# ============================================================================

@router.post(
    "/classify",
    response_model=EditClassificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Classify Edit Request",
    description="Classifies user edit request into one of four categories and returns structured prompt"
)
async def classify_edit_request(request: EditClassificationRequest):
    """
    Classify user edit request and prepare structured prompt for downstream agents
    
    Categories:
    - visual_edit: HTML/CSS styling changes
    - content_edit: Outline/content regeneration or RAG retrieval
    - cv_edit: Chart/plot/image data changes
    - regenerate_entire: Full presentation regeneration
    """
    start_time = time.time()
    
    try:
        logger.info(
            f"Received edit classification request for presentation {request.presentation_id}"
        )
        
        # Get agent instance
        agent = get_classifier_agent()
        
        # Classify the request
        result: EditClassificationResult = await agent.classify_async(
            user_request=request.user_request,
            session_id=request.session_id,
            presentation_id=request.presentation_id,
            user_id=request.user_id
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(
            f"Edit request classified as '{result.edit_request_class}' "
            f"in {processing_time:.2f}ms"
        )
        
        return EditClassificationResponse(
            success=True,
            id=request.id,
            presentation_id=result.presentation_id,
            session_id=result.session_id,
            user_id=result.user_id,
            edit_request_class=result.edit_request_class,
            modified_user_request=result.modified_user_request,
            processing_time_ms=processing_time,
            response="Edit request successfully classified"
        )
        
    except Exception as e:
        logger.error(f"Error in edit classification: {str(e)}")
        processing_time = (time.time() - start_time) * 1000
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Classification failed",
                "message": str(e),
                "processing_time_ms": processing_time
            }
        )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if Edit Request Classifier Agent is healthy and ready"
)
async def health_check():
    """Health check endpoint"""
    try:
        agent = get_classifier_agent()
        return HealthCheckResponse(
            status="healthy",
            agent="Edit Request Classifier Agent",
            timestamp=time.time()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "error": str(e)}
        )


@router.post(
    "/classify/batch",
    response_model=list[EditClassificationResponse],
    status_code=status.HTTP_200_OK,
    summary="Batch Classify Edit Requests",
    description="Classify multiple edit requests in a single batch operation"
)
async def batch_classify_edit_requests(requests: list[EditClassificationRequest]):
    """
    Batch classification endpoint for processing multiple edit requests
    
    Useful for:
    - Processing multiple pending edit requests
    - Bulk analysis of edit patterns
    - Testing classification accuracy
    """
    if len(requests) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch size cannot exceed 50 requests"
        )
    
    start_time = time.time()
    results = []
    
    try:
        agent = get_classifier_agent()
        
        for req in requests:
            try:
                result = await agent.classify_async(
                    user_request=req.user_request,
                    session_id=req.session_id,
                    presentation_id=req.presentation_id,
                    user_id=req.user_id
                )
                
                results.append(EditClassificationResponse(
                    success=True,
                    id=req.id,
                    presentation_id=result.presentation_id,
                    session_id=result.session_id,
                    user_id=result.user_id,
                    edit_request_class=result.edit_request_class,
                    modified_user_request=result.modified_user_request,
                    processing_time_ms=0,  # Individual timing not tracked in batch
                    response="Successfully classified"
                ))
            except Exception as e:
                logger.error(f"Error classifying request: {str(e)}")
                results.append(EditClassificationResponse(
                    success=False,
                    id=req.id,
                    presentation_id=req.presentation_id,
                    session_id=req.session_id,
                    user_id=req.user_id,
                    edit_request_class="content_edit",  # Safe default
                    modified_user_request=req.user_request,
                    processing_time_ms=0,
                    response=f"Classification failed: {str(e)}"
                ))
        
        total_time = (time.time() - start_time) * 1000
        logger.info(
            f"Batch classification completed: {len(results)} requests in {total_time:.2f}ms"
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Batch classification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Batch classification failed", "message": str(e)}
        )