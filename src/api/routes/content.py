"""API routes for Content Agent."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
import structlog

from src.db.mongodb import get_collection
from src.db.models import ContentAgentOutput, SlideContent
from src.agents.content.agent import ContentAgent
from src.agents.base import AgentRequest

logger = structlog.get_logger(__name__)

router = APIRouter()

# Request/Response Models
class ContentRequest(BaseModel):
    """Request model for content generation."""
    session_id: str = Field(..., alias="sessionId")
    user_id: str = Field(..., alias="userId")
    outline: Dict[str, Any]  # Outline from Outline Agent
    query_results: List[Dict[str, Any]] = Field(..., alias="queryResults")
    presentation_requirements: Dict[str, Any] = Field(..., alias="presentationRequirements")

    class Config:
        populate_by_name = True


class ContentResponse(BaseModel):
    """Response model for content generation."""
    success: bool
    session_id: str = Field(..., alias="sessionId")
    slides: List[Dict[str, Any]]
    total_slides: int = Field(..., alias="totalSlides")
    execution_time: float = Field(..., alias="executionTime")
    timestamp: str
    error: Optional[str] = None

    class Config:
        populate_by_name = True


@router.post("/content/generate", response_model=ContentResponse, tags=["agents"])
async def generate_content(
    content_request: ContentRequest = Body(...)
):
    """
    Generate detailed content for presentation slides.

    Takes outline and query results to create detailed content for each slide.
    """
    try:
        logger.info("content_agent_request_received", session_id=content_request.session_id)

        # Initialize Content Agent
        agent = ContentAgent()

        # Create agent request
        agent_request = AgentRequest(
            user_input="Generate presentation content from outline",
            context={
                "outline": content_request.outline,
                "query_results": content_request.query_results,
                "presentation_requirements": content_request.presentation_requirements
            },
            session_id=content_request.session_id
        )

        # Execute agent
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error("content_agent_execution_failed", errors=response.errors)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Content generation failed",
                    "errors": response.errors
                }
            )

        output = response.output

        # Save Content Agent output to MongoDB
        try:
            content_collection = get_collection("content_outputs")

            # Convert slides to SlideContent models
            slides = []
            for slide_data in output.get("slides", []):
                slides.append(SlideContent(
                    slideNumber=slide_data.get("slideNumber", 0),
                    title=slide_data.get("title", ""),
                    content=slide_data.get("content", {}),
                    dataPoints=slide_data.get("dataPoints", []),
                    citations=slide_data.get("citations", []),
                    speakerNotes=slide_data.get("speakerNotes")
                ))

            # Create Content Agent Output document
            content_output = ContentAgentOutput(
                slides=slides,
                totalSlides=output.get("total_slides", len(slides)),
                overallNarrative=output.get("overall_narrative"),
                keyTakeaways=output.get("key_takeaways", [])
            )

            # Save to MongoDB
            await content_collection.insert_one(
                content_output.model_dump(by_alias=True, exclude_none=False)
            )
            logger.info("content_output_saved_to_mongodb", session_id=content_request.session_id)

        except Exception as db_error:
            logger.error(
                "content_mongodb_save_failed",
                session_id=content_request.session_id,
                error=str(db_error),
                error_type=type(db_error).__name__
            )
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {str(db_error)}")

        logger.info("content_agent_completed", session_id=content_request.session_id)

        return ContentResponse(
            success=True,
            session_id=content_request.session_id,
            slides=output.get("slides", []),
            total_slides=output.get("total_slides", 0),
            execution_time=response.metadata.get("execution_time", 0.0),
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("content_agent_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
