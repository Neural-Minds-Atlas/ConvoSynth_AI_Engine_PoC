"""API routes for QA Agent."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
import structlog

from src.db.mongodb import get_collection
from src.db.models import QAAgentOutput, QAValidation
from src.agents.qa.agent import QAAgent
from src.agents.base import AgentRequest

logger = structlog.get_logger(__name__)

router = APIRouter()

# Request/Response Models
class QARequest(BaseModel):
    """Request model for QA validation."""
    session_id: str = Field(..., alias="sessionId")
    user_id: str = Field(..., alias="userId")
    presentation: Dict[str, Any]  # Full presentation data
    requirements: Dict[str, Any]  # Original requirements

    class Config:
        populate_by_name = True


class QAResponse(BaseModel):
    """Response model for QA validation."""
    success: bool
    session_id: str = Field(..., alias="sessionId")
    overall_score: float = Field(..., alias="overallScore")
    passed_validations: List[Dict[str, Any]] = Field(..., alias="passedValidations")
    failed_validations: List[Dict[str, Any]] = Field(..., alias="failedValidations")
    warnings: List[str]
    critical_issues: List[str] = Field(..., alias="criticalIssues")
    execution_time: float = Field(..., alias="executionTime")
    timestamp: str
    error: Optional[str] = None

    class Config:
        populate_by_name = True


@router.post("/qa/validate", response_model=QAResponse, tags=["agents"])
async def validate_presentation(
    request: QARequest = Body(...)
):
    """
    Perform quality assurance validation on presentation.

    Checks accuracy, completeness, consistency, and clarity of the presentation.
    """
    try:
        logger.info("qa_agent_request_received", session_id=request.session_id)

        # Initialize QA Agent
        agent = QAAgent()

        # Create agent request
        agent_request = AgentRequest(
            user_input="Validate presentation quality",
            context={
                "presentation": request.presentation,
                "requirements": request.requirements
            },
            session_id=request.session_id
        )

        # Execute agent
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error("qa_agent_failed", errors=response.errors)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "QA validation failed",
                    "errors": response.errors
                }
            )

        output = response.output

        # Save QA Agent output to MongoDB
        try:
            qa_collection = get_collection("qa_outputs")

            # Convert validations to models
            passed_validations = []
            for val_data in output.get("passed_validations", []):
                passed_validations.append(QAValidation(
                    category=val_data.get("category", ""),
                    status=val_data.get("status", "pass"),
                    issues=val_data.get("issues", []),
                    suggestions=val_data.get("suggestions", [])
                ))

            failed_validations = []
            for val_data in output.get("failed_validations", []):
                failed_validations.append(QAValidation(
                    category=val_data.get("category", ""),
                    status=val_data.get("status", "fail"),
                    issues=val_data.get("issues", []),
                    suggestions=val_data.get("suggestions", [])
                ))

            # Create QA Agent Output document
            qa_output = QAAgentOutput(
                overallScore=output.get("overall_score", 0.0),
                passedValidations=passed_validations,
                failedValidations=failed_validations,
                warnings=output.get("warnings", []),
                criticalIssues=output.get("critical_issues", []),
                recommendations=output.get("recommendations", [])
            )

            # Save to MongoDB
            await qa_collection.insert_one(
                qa_output.model_dump(by_alias=True, exclude_none=False)
            )
            logger.info("qa_output_saved_to_mongodb", session_id=request.session_id)

        except Exception as db_error:
            logger.error(
                "qa_mongodb_save_failed",
                session_id=request.session_id,
                error=str(db_error),
                error_type=type(db_error).__name__
            )
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {str(db_error)}")

        logger.info("qa_agent_completed", session_id=request.session_id, score=output.get("overall_score"))

        return QAResponse(
            success=True,
            session_id=request.session_id,
            overall_score=output.get("overall_score", 0.0),
            passed_validations=output.get("passed_validations", []),
            failed_validations=output.get("failed_validations", []),
            warnings=output.get("warnings", []),
            critical_issues=output.get("critical_issues", []),
            execution_time=response.metadata.get("execution_time", 0.0),
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("qa_agent_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
