"""Repository for workflow operations - Production Ready."""
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from src.db.mongodb import get_collection
from src.db.models import (
    WorkflowDocument,
    AgentExecutionMetadata,
    QueryAgentOutput,
    DocumentSelectionOutput,
    RAGEngineOutput,
    OutlineAgentOutput,
    ContentAgentOutput,
    ImageCoordinationOutput,
    FormatAgentOutput,
    QAAgentOutput,
    ValidationEngineOutput,
    ExtractedInformation,
)
from src.utils.logger import get_logger
from src.utils.exceptions import NotFoundException, DatabaseException

logger = get_logger(__name__)


class WorkflowRepository:
    """Repository for workflow CRUD operations with MongoDB."""

    def __init__(self):
        self.collection = get_collection("workflows")

    async def create_workflow(
        self,
        session_id: str,
        user_id: str,
        user_input: str,
        documents: List[str] = None,
        user_preferences: Dict[str, Any] = None,
    ) -> WorkflowDocument:
        """Create a new workflow.

        Args:
            session_id: Conversation session ID
            user_id: User ID
            user_input: User's initial input
            documents: List of document paths/IDs
            user_preferences: User preferences

        Returns:
            Created workflow document

        Raises:
            DatabaseException: If creation fails
        """
        try:
            workflow_id = f"wf-{uuid.uuid4()}"

            workflow = WorkflowDocument(
                workflowId=workflow_id,
                sessionId=session_id,
                userId=user_id,
                userInput=user_input,
                documents=documents or [],
                userPreferences=user_preferences or {},
                status="in_progress",
                currentStage="conversation",
                startedAt=datetime.utcnow(),
            )

            # Convert to dict and insert
            workflow_dict = workflow.model_dump(by_alias=True, exclude_none=False)

            result = await self.collection.insert_one(workflow_dict)

            if not result.inserted_id:
                raise DatabaseException("Failed to create workflow", details={"workflow_id": workflow_id})

            logger.info("workflow_created", workflow_id=workflow_id, user_id=user_id)

            return workflow

        except Exception as e:
            logger.error("workflow_creation_failed", error=str(e), user_id=user_id)
            raise DatabaseException(f"Failed to create workflow: {str(e)}")

    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDocument]:
        """Get workflow by ID.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow document or None

        Raises:
            NotFoundException: If workflow not found
        """
        try:
            workflow_dict = await self.collection.find_one({"workflowId": workflow_id})

            if not workflow_dict:
                raise NotFoundException("Workflow", workflow_id)

            # Remove MongoDB _id for cleaner response
            workflow_dict.pop("_id", None)

            return WorkflowDocument(**workflow_dict)

        except NotFoundException:
            raise
        except Exception as e:
            logger.error("workflow_fetch_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to fetch workflow: {str(e)}")

    async def update_stage(
        self,
        workflow_id: str,
        stage: str,
        agent_execution: AgentExecutionMetadata,
    ) -> bool:
        """Update workflow stage and add agent execution metadata.

        Args:
            workflow_id: Workflow ID
            stage: Current stage name
            agent_execution: Agent execution metadata

        Returns:
            True if updated successfully

        Raises:
            DatabaseException: If update fails
        """
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "currentStage": stage,
                        "updatedAt": datetime.utcnow(),
                    },
                    "$push": {
                        "agentExecutions": agent_execution.model_dump(by_alias=True)
                    },
                    "$inc": {
                        "totalTokensUsed": agent_execution.tokenUsage or 0
                    },
                }
            )

            if result.modified_count == 0:
                raise DatabaseException("Failed to update workflow stage", details={"workflow_id": workflow_id})

            logger.info(
                "workflow_stage_updated",
                workflow_id=workflow_id,
                stage=stage,
                agent=agent_execution.agentName
            )

            return True

        except Exception as e:
            logger.error("workflow_stage_update_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to update workflow stage: {str(e)}")

    async def update_query_agent_output(
        self,
        workflow_id: str,
        output: QueryAgentOutput,
    ) -> bool:
        """Update workflow with Query Agent output.

        Args:
            workflow_id: Workflow ID
            output: Query Agent output

        Returns:
            True if updated

        Raises:
            DatabaseException: If update fails
        """
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "queryAgentOutput": output.model_dump(by_alias=True),
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            if result.modified_count == 0:
                raise DatabaseException("Failed to update query agent output")

            logger.info("query_agent_output_saved", workflow_id=workflow_id)
            return True

        except Exception as e:
            logger.error("query_agent_output_save_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to save query agent output: {str(e)}")

    async def update_document_selection_output(
        self,
        workflow_id: str,
        output: DocumentSelectionOutput,
    ) -> bool:
        """Update workflow with Document Selection Agent output."""
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "documentSelectionOutput": output.model_dump(by_alias=True),
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error("document_selection_output_save_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to save document selection output: {str(e)}")

    async def update_rag_engine_output(
        self,
        workflow_id: str,
        output: RAGEngineOutput,
    ) -> bool:
        """Update workflow with RAG Engine output."""
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "ragEngineOutput": output.model_dump(by_alias=True),
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error("rag_engine_output_save_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to save RAG engine output: {str(e)}")

    async def update_outline_agent_output(
        self,
        workflow_id: str,
        output: OutlineAgentOutput,
    ) -> bool:
        """Update workflow with Outline Agent output."""
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "outlineAgentOutput": output.model_dump(by_alias=True),
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error("outline_agent_output_save_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to save outline agent output: {str(e)}")

    async def update_content_agent_output(
        self,
        workflow_id: str,
        output: ContentAgentOutput,
    ) -> bool:
        """Update workflow with Content Agent output."""
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "contentAgentOutput": output.model_dump(by_alias=True),
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error("content_agent_output_save_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to save content agent output: {str(e)}")

    async def update_image_coordination_output(
        self,
        workflow_id: str,
        output: ImageCoordinationOutput,
    ) -> bool:
        """Update workflow with Image Coordination Agent output."""
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "imageCoordinationOutput": output.model_dump(by_alias=True),
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error("image_coordination_output_save_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to save image coordination output: {str(e)}")

    async def update_format_agent_output(
        self,
        workflow_id: str,
        output: FormatAgentOutput,
    ) -> bool:
        """Update workflow with Format Agent output."""
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "formatAgentOutput": output.model_dump(by_alias=True),
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error("format_agent_output_save_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to save format agent output: {str(e)}")

    async def update_qa_agent_output(
        self,
        workflow_id: str,
        output: QAAgentOutput,
    ) -> bool:
        """Update workflow with QA Agent output."""
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "qaAgentOutput": output.model_dump(by_alias=True),
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error("qa_agent_output_save_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to save QA agent output: {str(e)}")

    async def update_validation_engine_output(
        self,
        workflow_id: str,
        output: ValidationEngineOutput,
    ) -> bool:
        """Update workflow with Validation Engine output."""
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "validationEngineOutput": output.model_dump(by_alias=True),
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error("validation_engine_output_save_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to save validation engine output: {str(e)}")

    async def complete_workflow(
        self,
        workflow_id: str,
        final_presentation: Dict[str, Any],
        presentation_html: str,
        total_execution_time: float,
    ) -> bool:
        """Mark workflow as completed and save final output.

        Args:
            workflow_id: Workflow ID
            final_presentation: Final presentation data
            presentation_html: Complete HTML output
            total_execution_time: Total execution time in seconds

        Returns:
            True if completed successfully

        Raises:
            DatabaseException: If update fails
        """
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "status": "completed",
                        "currentStage": "completed",
                        "finalPresentation": final_presentation,
                        "presentationHtml": presentation_html,
                        "completedAt": datetime.utcnow(),
                        "totalExecutionTime": total_execution_time,
                        "updatedAt": datetime.utcnow(),
                    }
                }
            )

            if result.modified_count == 0:
                raise DatabaseException("Failed to complete workflow")

            logger.info(
                "workflow_completed",
                workflow_id=workflow_id,
                execution_time=total_execution_time
            )

            return True

        except Exception as e:
            logger.error("workflow_completion_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to complete workflow: {str(e)}")

    async def fail_workflow(
        self,
        workflow_id: str,
        failed_stage: str,
        error_message: str,
    ) -> bool:
        """Mark workflow as failed.

        Args:
            workflow_id: Workflow ID
            failed_stage: Stage where failure occurred
            error_message: Error message

        Returns:
            True if updated

        Raises:
            DatabaseException: If update fails
        """
        try:
            result = await self.collection.update_one(
                {"workflowId": workflow_id},
                {
                    "$set": {
                        "status": "failed",
                        "failedStage": failed_stage,
                        "completedAt": datetime.utcnow(),
                        "updatedAt": datetime.utcnow(),
                    },
                    "$push": {
                        "errors": {
                            "stage": failed_stage,
                            "message": error_message,
                            "timestamp": datetime.utcnow(),
                        }
                    }
                }
            )

            if result.modified_count == 0:
                raise DatabaseException("Failed to mark workflow as failed")

            logger.error(
                "workflow_failed",
                workflow_id=workflow_id,
                failed_stage=failed_stage,
                error=error_message
            )

            return True

        except Exception as e:
            logger.error("workflow_failure_update_failed", error=str(e), workflow_id=workflow_id)
            raise DatabaseException(f"Failed to update workflow failure: {str(e)}")

    async def get_user_workflows(
        self,
        user_id: str,
        limit: int = 20,
        skip: int = 0,
    ) -> List[WorkflowDocument]:
        """Get workflows for a user.

        Args:
            user_id: User ID
            limit: Maximum number of workflows to return
            skip: Number of workflows to skip

        Returns:
            List of workflow documents

        Raises:
            DatabaseException: If fetch fails
        """
        try:
            cursor = self.collection.find(
                {"userId": user_id}
            ).sort("createdAt", -1).skip(skip).limit(limit)

            workflows = []
            async for workflow_dict in cursor:
                workflow_dict.pop("_id", None)
                workflows.append(WorkflowDocument(**workflow_dict))

            logger.info("user_workflows_fetched", user_id=user_id, count=len(workflows))

            return workflows

        except Exception as e:
            logger.error("user_workflows_fetch_failed", error=str(e), user_id=user_id)
            raise DatabaseException(f"Failed to fetch user workflows: {str(e)}")

    async def get_workflow_statistics(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Get workflow performance statistics.

        Args:
            workflow_id: Workflow ID

        Returns:
            Dictionary with statistics

        Raises:
            NotFoundException: If workflow not found
        """
        workflow = await self.get_workflow(workflow_id)

        stats = {
            "workflow_id": workflow_id,
            "status": workflow.status,
            "total_execution_time": workflow.totalExecutionTime,
            "total_tokens_used": workflow.totalTokensUsed,
            "agent_count": len(workflow.agentExecutions),
            "latency_breakdown": workflow.latencyBreakdown,
            "success_rate": sum(1 for ex in workflow.agentExecutions if ex.success) / len(workflow.agentExecutions) if workflow.agentExecutions else 0,
        }

        return stats
