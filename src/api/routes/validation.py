"""API routes for Validation Engine Agent."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
import structlog

from src.db.mongodb import get_collection
from src.db.models import ValidationEngineOutput, ValidationResult
from src.agents.validation.agent import ValidationAgent
from src.agents.base import AgentRequest

logger = structlog.get_logger(__name__)

router = APIRouter()

# Request/Response Models
class ValidationRequest(BaseModel):
    """Request model for validation."""
    session_id: str = Field(..., alias="sessionId")
    user_id: str = Field(..., alias="userId")
    presentation: Dict[str, Any]  # Full presentation to validate
    qa_results: Optional[Dict[str, Any]] = Field(default=None, alias="qaResults")  # From QA Agent

    class Config:
        populate_by_name = True


class ValidationResponse(BaseModel):
    """Response model for validation."""
    success: bool
    session_id: str = Field(..., alias="sessionId")
    is_valid: bool = Field(..., alias="isValid")
    validation_results: List[Dict[str, Any]] = Field(..., alias="validationResults")
    overall_score: float = Field(..., alias="overallScore")
    ready_for_delivery: bool = Field(..., alias="readyForDelivery")
    issues: List[str]
    execution_time: float = Field(..., alias="executionTime")
    timestamp: str
    error: Optional[str] = None

    class Config:
        populate_by_name = True


@router.post("/validation/validate", response_model=ValidationResponse, tags=["agents"])
async def validate_final_presentation(
    request: ValidationRequest = Body(...)
):
    """
    Perform final validation on presentation.

    Validates completeness, format, accessibility, and business rules.
    Determines if presentation is ready for delivery.
    """
    try:
        logger.info("validation_agent_request_received", session_id=request.session_id)

        # Initialize Validation Agent
        agent = ValidationAgent()

        # Create agent request
        agent_request = AgentRequest(
            user_input="Perform final validation on presentation",
            context={
                "presentation": request.presentation,
                "qa_results": request.qa_results or {}
            },
            session_id=request.session_id
        )

        # Execute agent
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error("validation_agent_failed", errors=response.errors)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Validation failed",
                    "errors": response.errors
                }
            )

        output = response.output

        # Save Validation Engine output to MongoDB
        try:
            validation_collection = get_collection("validation_outputs")

            # Convert validation results to models
            validation_results = []
            for result_data in output.get("validation_results", []):
                validation_results.append(ValidationResult(
                    validationType=result_data.get("validation_type", ""),
                    passed=result_data.get("passed", False),
                    message=result_data.get("message", ""),
                    details=result_data.get("details", {})
                ))

            # Create Validation Engine Output document
            validation_output = ValidationEngineOutput(
                isValid=output.get("is_valid", False),
                validationResults=validation_results,
                overallScore=output.get("overall_score", 0.0),
                readyForDelivery=output.get("ready_for_delivery", False),
                issues=output.get("issues", [])
            )

            # Save to MongoDB
            await validation_collection.insert_one(
                validation_output.model_dump(by_alias=True, exclude_none=False)
            )
            logger.info(
                "validation_output_saved_to_mongodb",
                session_id=request.session_id,
                ready=output.get("ready_for_delivery")
            )

        except Exception as db_error:
            logger.error(
                "validation_mongodb_save_failed",
                session_id=request.session_id,
                error=str(db_error),
                error_type=type(db_error).__name__
            )
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {str(db_error)}")

        logger.info(
            "validation_agent_completed",
            session_id=request.session_id,
            valid=output.get("is_valid"),
            score=output.get("overall_score")
        )

        return ValidationResponse(
            success=True,
            session_id=request.session_id,
            is_valid=output.get("is_valid", False),
            validation_results=output.get("validation_results", []),
            overall_score=output.get("overall_score", 0.0),
            ready_for_delivery=output.get("ready_for_delivery", False),
            issues=output.get("issues", []),
            execution_time=response.metadata.get("execution_time", 0.0),
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("validation_agent_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
