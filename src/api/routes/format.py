"""API routes for Format Agent."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
import structlog

from src.db.mongodb import get_collection
from src.db.models import FormatAgentOutput, FormattedSlide
from src.agents.format.agent import FormatAgent
from src.agents.base import AgentRequest

logger = structlog.get_logger(__name__)

router = APIRouter()

# Request/Response Models
class FormatRequest(BaseModel):
    """Request model for formatting."""
    session_id: str = Field(..., alias="sessionId")
    user_id: str = Field(..., alias="userId")
    slides: List[Dict[str, Any]]  # Slides from Content Agent
    visual_specs: List[Dict[str, Any]] = Field(..., alias="visualSpecs")  # From Image Coordination
    theme: str = "professional"

    class Config:
        populate_by_name = True


class FormatResponse(BaseModel):
    """Response model for formatting."""
    success: bool
    session_id: str = Field(..., alias="sessionId")
    slides: List[Dict[str, Any]]
    full_html: str = Field(..., alias="fullHtml")
    total_slides: int = Field(..., alias="totalSlides")
    execution_time: float = Field(..., alias="executionTime")
    timestamp: str
    error: Optional[str] = None

    class Config:
        populate_by_name = True


@router.post("/format/generate", response_model=FormatResponse, tags=["agents"])
async def format_presentation(
    request: FormatRequest = Body(...)
):
    """
    Format presentation slides into HTML.

    Converts slide content and visual specs into formatted HTML presentation.
    """
    try:
        logger.info("format_agent_request_received", session_id=request.session_id)

        # Initialize Format Agent
        agent = FormatAgent()

        # Create agent request
        agent_request = AgentRequest(
            user_input="Format slides into HTML presentation",
            context={
                "slides": request.slides,
                "visual_specs": request.visual_specs,
                "theme": request.theme
            },
            session_id=request.session_id
        )

        # Execute agent
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error("format_agent_failed", errors=response.errors)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Formatting failed",
                    "errors": response.errors
                }
            )

        output = response.output

        # Save Format Agent output to MongoDB
        try:
            format_collection = get_collection("format_outputs")

            # Convert formatted slides to models
            formatted_slides = []
            for slide_data in output.get("slides", []):
                formatted_slides.append(FormattedSlide(
                    slideNumber=slide_data.get("slideNumber", 0),
                    html=slide_data.get("html", ""),
                    cssClasses=slide_data.get("cssClasses", []),
                    visualElements=slide_data.get("visualElements", [])
                ))

            # Create Format Agent Output document
            format_output = FormatAgentOutput(
                slides=formatted_slides,
                fullHtml=output.get("full_html", ""),
                cssStyles=output.get("css_styles", ""),
                totalSlides=output.get("total_slides", len(formatted_slides)),
                theme=request.theme
            )

            # Save to MongoDB
            await format_collection.insert_one(
                format_output.model_dump(by_alias=True, exclude_none=False)
            )
            logger.info("format_output_saved_to_mongodb", session_id=request.session_id)

        except Exception as db_error:
            logger.error(
                "format_mongodb_save_failed",
                session_id=request.session_id,
                error=str(db_error),
                error_type=type(db_error).__name__
            )
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {str(db_error)}")

        logger.info("format_agent_completed", session_id=request.session_id)

        return FormatResponse(
            success=True,
            session_id=request.session_id,
            slides=output.get("slides", []),
            full_html=output.get("full_html", ""),
            total_slides=output.get("total_slides", 0),
            execution_time=response.metadata.get("execution_time", 0.0),
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("format_agent_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
