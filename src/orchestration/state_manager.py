"""State management for workflow orchestration."""
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class WorkflowStage(str, Enum):
    """Workflow stages."""
    CONVERSATION = "conversation"
    QUERY = "query"
    RAG_RETRIEVAL = "rag_retrieval"
    OUTLINE = "outline"
    CONTENT = "content"
    IMAGE_GENERATION = "image_generation"
    FORMATTING = "formatting"
    QA_VALIDATION = "qa_validation"
    FINAL_VALIDATION = "final_validation"


class WorkflowState:
    """Represents the state of a workflow execution."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.utcnow()
        self.stages: Dict[WorkflowStage, Dict[str, Any]] = {}
        self.status = "running"
        self.error: Optional[str] = None
        self.completed_at: Optional[datetime] = None
        self.total_time: Optional[float] = None


class StateManager:
    """Manages workflow state across execution."""

    def __init__(self):
        self.states: Dict[str, WorkflowState] = {}
        self.logger = logger.bind(component="state_manager")

    def create_state(self, session_id: str) -> WorkflowState:
        """Create a new workflow state."""
        state = WorkflowState(session_id)
        self.states[session_id] = state
        self.logger.info("state_created", session_id=session_id)
        return state

    def get_state(self, session_id: str) -> Optional[WorkflowState]:
        """Get workflow state by session ID."""
        return self.states.get(session_id)

    def update_stage(
        self,
        session_id: str,
        stage: WorkflowStage,
        data: Dict[str, Any]
    ) -> None:
        """Update a specific stage with data."""
        state = self.states.get(session_id)
        if state:
            state.stages[stage] = {
                "data": data,
                "completed_at": datetime.utcnow(),
            }
            self.logger.debug(
                "stage_updated",
                session_id=session_id,
                stage=stage.value
            )

    def mark_completed(self, session_id: str, total_time: float) -> None:
        """Mark workflow as completed."""
        state = self.states.get(session_id)
        if state:
            state.status = "completed"
            state.completed_at = datetime.utcnow()
            state.total_time = total_time
            self.logger.info(
                "workflow_completed",
                session_id=session_id,
                total_time=total_time
            )

    def mark_failed(self, session_id: str, error: str) -> None:
        """Mark workflow as failed."""
        state = self.states.get(session_id)
        if state:
            state.status = "failed"
            state.error = error
            state.completed_at = datetime.utcnow()
            self.logger.error(
                "workflow_failed",
                session_id=session_id,
                error=error
            )
