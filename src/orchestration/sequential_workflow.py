"""Sequential workflow orchestrator for 20-second presentation generation."""
import time
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
import structlog

from src.config.settings import get_settings
from .state_manager import StateManager, WorkflowStage

logger = structlog.get_logger(__name__)
settings = get_settings()


class SequentialWorkflow:
    """Orchestrates sequential execution of 9 agents for presentation generation.

    Target: 20 seconds total latency
    Sequential Flow:
    1. Conversation Agent (2s) - Extract requirements
    2. Query Agent (2s) - Parse intent
    3. RAG Engine (3s) - Retrieve context
    4. Outline Agent (2s) - Generate structure
    5. Content Agent (4s) - Expand content
    6. Image Coordination (3s) - Generate visuals
    7. Format Agent (2s) - Create HTML
    8. QA Agent (1s) - Validate accuracy
    9. Validation Engine (1s) - Final check
    """

    def __init__(self, rag_client=None):
        """Initialize sequential workflow.

        Args:
            rag_client: Optional RAG client (will be created if not provided)
        """
        self.state_manager = StateManager()
        self.logger = logger.bind(component="sequential_workflow")

        # Store RAG client for agent initialization
        self._rag_client = rag_client

        # Agents will be initialized later (lazy loading)
        self._conversation_agent = None
        self._query_agent = None
        self._rag_engine = None
        self._outline_agent = None
        self._content_agent = None
        self._image_coordinator = None
        self._format_agent = None
        self._qa_agent = None
        self._validation_engine = None

    async def execute(
        self,
        user_input: str,
        documents: Optional[List[Path]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute complete sequential workflow.

        Args:
            user_input: User's presentation request
            documents: Optional list of document paths
            user_preferences: Optional user preferences

        Returns:
            Final presentation output with metadata

        Raises:
            WorkflowError: If workflow execution fails
        """
        session_id = str(uuid.uuid4())
        start_time = time.time()

        self.logger.info(
            "workflow_started",
            session_id=session_id,
            has_documents=documents is not None,
            document_count=len(documents) if documents else 0,
        )

        # Create workflow state
        state = self.state_manager.create_state(session_id)

        try:
            # Phase 1: Conversation Agent (2s target)
            requirements = await self._run_conversation_agent(
                session_id, user_input, state
            )

            # Phase 2: Query Agent (2s target)
            query_output = await self._run_query_agent(
                session_id, requirements, state
            )

            # Phase 3: RAG Engine (3s target)
            rag_context = await self._run_rag_engine(
                session_id, query_output, documents, state
            )

            # Phase 4: Outline Agent (2s target)
            outline = await self._run_outline_agent(
                session_id, rag_context, requirements, state
            )

            # Phase 5: Content Agent (4s target)
            content = await self._run_content_agent(
                session_id, outline, rag_context, state
            )

            # Phase 6: Image Coordination (3s target)
            images = await self._run_image_coordinator(
                session_id, content, state
            )

            # Phase 7: Format Agent (2s target)
            html_output = await self._run_format_agent(
                session_id, content, images, user_preferences, state
            )

            # Phase 8: QA Agent (1s target)
            qa_result = await self._run_qa_agent(
                session_id, html_output, rag_context, state
            )

            # Phase 9: Validation Engine (1s target)
            final_output = await self._run_validation_engine(
                session_id, html_output, qa_result, requirements, state
            )

            total_time = time.time() - start_time
            self.state_manager.mark_completed(session_id, total_time)

            self.logger.info(
                "workflow_completed",
                session_id=session_id,
                total_time=total_time,
                target_time=settings.total_latency_target_seconds,
                within_target=total_time <= settings.total_latency_target_seconds,
            )

            return {
                "session_id": session_id,
                "presentation": final_output,
                "metadata": {
                    "total_time": total_time,
                    "target_time": settings.total_latency_target_seconds,
                    "within_target": total_time <= settings.total_latency_target_seconds,
                    "stage_timings": self._extract_stage_timings(state),
                },
            }

        except Exception as e:
            self.logger.error(
                "workflow_failed",
                session_id=session_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            self.state_manager.mark_failed(session_id, str(e))
            raise

    async def _run_conversation_agent(
        self, session_id: str, user_input: str, state: Any
    ) -> Dict[str, Any]:
        """Run Conversation Agent.

        Args:
            session_id: Session ID
            user_input: User input
            state: Workflow state

        Returns:
            Extracted requirements
        """
        self.logger.info("stage_started", session_id=session_id, stage="conversation")
        start_time = time.time()

        # TODO: Implement actual agent call
        # For now, return placeholder
        requirements = {
            "user_input": user_input,
            "presentation_type": "financial",
            "slide_count": 8,
            "missing_info": [],
            "complete": True,
        }

        elapsed = time.time() - start_time
        self.state_manager.update_stage(
            session_id, WorkflowStage.CONVERSATION, requirements
        )

        self.logger.info(
            "stage_completed",
            session_id=session_id,
            stage="conversation",
            elapsed=elapsed,
            target=settings.conversation_agent_timeout,
        )

        return requirements

    async def _run_query_agent(
        self, session_id: str, requirements: Dict[str, Any], state: Any
    ) -> Dict[str, Any]:
        """Run Query Agent."""
        self.logger.info("stage_started", session_id=session_id, stage="query")
        start_time = time.time()

        # TODO: Implement actual agent
        query_output = {
            "intent": "generate_financial_presentation",
            "entities": {},
            "query_context": requirements,
            "confidence": 0.95,
        }

        elapsed = time.time() - start_time
        self.state_manager.update_stage(session_id, WorkflowStage.QUERY, query_output)

        self.logger.info(
            "stage_completed",
            session_id=session_id,
            stage="query",
            elapsed=elapsed,
        )

        return query_output

    async def _run_rag_engine(
        self,
        session_id: str,
        query_output: Dict[str, Any],
        documents: Optional[List[Path]],
        state: Any,
    ) -> Dict[str, Any]:
        """Run RAG Engine with actual document retrieval."""
        self.logger.info("stage_started", session_id=session_id, stage="rag_engine")
        start_time = time.time()

        # Initialize RAG engine if needed (lazy loading)
        if self._rag_engine is None:
            from src.agents.rag_engine import RAGEngineAgent
            self._rag_engine = RAGEngineAgent(rag_client=self._rag_client)

            # Initialize if not already done
            if self._rag_client and not self._rag_client._initialized:
                await self._rag_engine.initialize()

        # Create agent request
        from src.agents.base import AgentRequest

        request = AgentRequest(
            user_input=query_output.get("query_context", {}).get("primary_focus", ""),
            context={
                "query_output": query_output,
                "documents": documents or [],
                "session_id": session_id,
            }
        )

        # Execute RAG retrieval
        try:
            rag_context = await self._rag_engine.execute(request)

            self.logger.info(
                "rag_retrieval_executed",
                session_id=session_id,
                context_length=len(rag_context.get("retrieved_context", "")),
                sources_count=len(rag_context.get("sources", [])),
            )

        except Exception as e:
            self.logger.error(
                "rag_engine_failed",
                session_id=session_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            # Fallback to empty context
            rag_context = {
                "retrieved_context": f"RAG retrieval failed: {str(e)}",
                "sources": [],
                "relevance_scores": {},
                "knowledge_graph_entities": [],
                "error": str(e),
            }

        elapsed = time.time() - start_time
        self.state_manager.update_stage(
            session_id, WorkflowStage.RAG_RETRIEVAL, rag_context
        )

        self.logger.info(
            "stage_completed",
            session_id=session_id,
            stage="rag_engine",
            elapsed=elapsed,
        )

        return rag_context

    async def _run_outline_agent(
        self,
        session_id: str,
        rag_context: Dict[str, Any],
        requirements: Dict[str, Any],
        state: Any,
    ) -> Dict[str, Any]:
        """Run Outline Agent."""
        self.logger.info("stage_started", session_id=session_id, stage="outline")
        start_time = time.time()

        # TODO: Implement actual agent
        outline = {
            "slides": [],
            "total_slides": 8,
            "presentation_flow": "Introduction -> Analysis -> Conclusion",
        }

        elapsed = time.time() - start_time
        self.state_manager.update_stage(session_id, WorkflowStage.OUTLINE, outline)

        self.logger.info(
            "stage_completed",
            session_id=session_id,
            stage="outline",
            elapsed=elapsed,
        )

        return outline

    async def _run_content_agent(
        self,
        session_id: str,
        outline: Dict[str, Any],
        rag_context: Dict[str, Any],
        state: Any,
    ) -> Dict[str, Any]:
        """Run Content Agent."""
        self.logger.info("stage_started", session_id=session_id, stage="content")
        start_time = time.time()

        # TODO: Implement actual agent
        content = {
            "slide_contents": [],
            "financial_data": {},
            "calculations": {},
        }

        elapsed = time.time() - start_time
        self.state_manager.update_stage(session_id, WorkflowStage.CONTENT, content)

        self.logger.info(
            "stage_completed",
            session_id=session_id,
            stage="content",
            elapsed=elapsed,
        )

        return content

    async def _run_image_coordinator(
        self, session_id: str, content: Dict[str, Any], state: Any
    ) -> Dict[str, Any]:
        """Run Image Coordination Agent."""
        self.logger.info("stage_started", session_id=session_id, stage="image_coordination")
        start_time = time.time()

        # TODO: Implement actual agent
        images = {
            "images": [],
            "charts": [],
            "visual_assets": {},
        }

        elapsed = time.time() - start_time
        self.state_manager.update_stage(
            session_id, WorkflowStage.IMAGE_GENERATION, images
        )

        self.logger.info(
            "stage_completed",
            session_id=session_id,
            stage="image_coordination",
            elapsed=elapsed,
        )

        return images

    async def _run_format_agent(
        self,
        session_id: str,
        content: Dict[str, Any],
        images: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]],
        state: Any,
    ) -> Dict[str, Any]:
        """Run Format Agent."""
        self.logger.info("stage_started", session_id=session_id, stage="format")
        start_time = time.time()

        # TODO: Implement actual agent
        html_output = {
            "html_content": "<html>...</html>",
            "css_styles": "...",
            "assets": {},
        }

        elapsed = time.time() - start_time
        self.state_manager.update_stage(session_id, WorkflowStage.FORMATTING, html_output)

        self.logger.info(
            "stage_completed",
            session_id=session_id,
            stage="format",
            elapsed=elapsed,
        )

        return html_output

    async def _run_qa_agent(
        self,
        session_id: str,
        html_output: Dict[str, Any],
        rag_context: Dict[str, Any],
        state: Any,
    ) -> Dict[str, Any]:
        """Run QA Agent."""
        self.logger.info("stage_started", session_id=session_id, stage="qa")
        start_time = time.time()

        # TODO: Implement actual agent
        qa_result = {
            "validation_passed": True,
            "errors": [],
            "warnings": [],
            "accuracy_score": 0.98,
        }

        elapsed = time.time() - start_time
        self.state_manager.update_stage(session_id, WorkflowStage.QA_VALIDATION, qa_result)

        self.logger.info(
            "stage_completed",
            session_id=session_id,
            stage="qa",
            elapsed=elapsed,
        )

        return qa_result

    async def _run_validation_engine(
        self,
        session_id: str,
        html_output: Dict[str, Any],
        qa_result: Dict[str, Any],
        requirements: Dict[str, Any],
        state: Any,
    ) -> Dict[str, Any]:
        """Run Validation Engine."""
        self.logger.info("stage_started", session_id=session_id, stage="validation")
        start_time = time.time()

        # TODO: Implement actual engine
        final_output = {
            "is_complete": True,
            "completeness_score": 1.0,
            "issues": [],
            "final_output": html_output["html_content"],
        }

        elapsed = time.time() - start_time
        self.state_manager.update_stage(
            session_id, WorkflowStage.FINAL_VALIDATION, final_output
        )

        self.logger.info(
            "stage_completed",
            session_id=session_id,
            stage="validation",
            elapsed=elapsed,
        )

        return final_output

    def _extract_stage_timings(self, state: Any) -> Dict[str, float]:
        """Extract timing information for each stage."""
        # TODO: Implement actual timing extraction
        return {}
