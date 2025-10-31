"""API routes for Image Coordination Agent."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
import structlog

from src.db.mongodb import get_collection
from src.db.models import ImageCoordinationOutput, VisualSpecification
from src.agents.image_coordination.agent import ImageCoordinationAgent
from src.agents.base import AgentRequest

logger = structlog.get_logger(__name__)

router = APIRouter()

# Request/Response Models
class ImageCoordinationRequest(BaseModel):
    """Request model for image coordination."""
    session_id: str = Field(..., alias="sessionId")
    user_id: str = Field(..., alias="userId")
    slides: List[Dict[str, Any]]  # Slides from Content Agent
    visual_preferences: Dict[str, Any] = Field(..., alias="visualPreferences")

    class Config:
        populate_by_name = True


class ImageCoordinationResponse(BaseModel):
    """Response model for image coordination."""
    success: bool
    session_id: str = Field(..., alias="sessionId")
    visual_specs: List[Dict[str, Any]] = Field(..., alias="visualSpecs")
    total_visuals: int = Field(..., alias="totalVisuals")
    execution_time: float = Field(..., alias="executionTime")
    timestamp: str
    error: Optional[str] = None

    class Config:
        populate_by_name = True


@router.post("/image-coordination/generate", response_model=ImageCoordinationResponse, tags=["agents"])
async def coordinate_images(
    request: ImageCoordinationRequest = Body(...)
):
    """
    Coordinate visual specifications for presentation slides.

    Analyzes content and creates specifications for charts, graphs, and images.
    """
    try:
        logger.info("image_coordination_request_received", session_id=request.session_id)

        # Initialize Image Coordination Agent
        agent = ImageCoordinationAgent()

        # Create agent request
        agent_request = AgentRequest(
            user_input="Generate visual specifications for slides",
            context={
                "slides": request.slides,
                "visual_preferences": request.visual_preferences
            },
            session_id=request.session_id
        )

        # Execute agent
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error("image_coordination_failed", errors=response.errors)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Image coordination failed",
                    "errors": response.errors
                }
            )

        output = response.output

        # Save Image Coordination output to MongoDB
        try:
            image_collection = get_collection("image_coordination_outputs")

            # Convert visual specs to models
            visual_specs = []
            for spec_data in output.get("visual_specs", []):
                visual_specs.append(VisualSpecification(
                    slideNumber=spec_data.get("slideNumber", 0),
                    visualType=spec_data.get("visualType", "chart"),
                    chartType=spec_data.get("chartType"),
                    dataSource=spec_data.get("dataSource", ""),
                    title=spec_data.get("title", ""),
                    description=spec_data.get("description", ""),
                    specifications=spec_data.get("specifications", {})
                ))

            # Create Image Coordination Output document
            image_output = ImageCoordinationOutput(
                visualSpecs=visual_specs,
                totalVisuals=output.get("total_visuals", len(visual_specs)),
                visualTheme=output.get("visual_theme", "professional"),
                colorScheme=output.get("color_scheme", [])
            )

            # Save to MongoDB
            await image_collection.insert_one(
                image_output.model_dump(by_alias=True, exclude_none=False)
            )
            logger.info("image_coordination_saved_to_mongodb", session_id=request.session_id)

        except Exception as db_error:
            logger.error(
                "image_coordination_mongodb_save_failed",
                session_id=request.session_id,
                error=str(db_error),
                error_type=type(db_error).__name__
            )
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {str(db_error)}")

        logger.info("image_coordination_completed", session_id=request.session_id)

        return ImageCoordinationResponse(
            success=True,
            session_id=request.session_id,
            visual_specs=output.get("visual_specs", []),
            total_visuals=output.get("total_visuals", 0),
            execution_time=response.metadata.get("execution_time", 0.0),
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("image_coordination_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
