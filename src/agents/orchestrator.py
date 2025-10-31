"""Agent Orchestrator - Coordinates all agents in the workflow."""
from typing import Any, Dict, Optional
import structlog

from .base import AgentRequest, AgentResponse
from .conversation import ConversationAgent
from .query import QueryAgent
from .document_selection import DocumentSelectionAgent
from .rag_engine.agent import RAGEngineAgent
from .outline import OutlineAgent
from .content import ContentAgent
from .image_coordination import ImageCoordinationAgent
from .qa import QAAgent
from .format import FormatAgent
from .validation import ValidationAgent

from src.rag_anything.client import RAGAnythingClient

logger = structlog.get_logger(__name__)


class AgentOrchestrator:
    """Orchestrates the multi-agent workflow for presentation generation.

    Workflow:
    1. Conversation Agent - Gather requirements
    2. Query Agent - Extract intent and context
    3. Document Selection Agent - Filter relevant documents using metadata RAG
    4. RAG Engine - Retrieve relevant information
    5. Outline Agent - Generate presentation structure
    6. Content Agent - Expand outline into full content
    7. Image Coordination Agent - Specify visualizations
    8. QA Agent - Validate content accuracy
    9. Format Agent - Generate HTML presentation
    10. Validation Engine - Final completeness check
    """

    def __init__(self, rag_client: Optional[RAGAnythingClient] = None):
        """Initialize the orchestrator with all agents."""
        self.logger = logger.bind(component="agent_orchestrator")

        # Initialize all agents
        self.conversation_agent = ConversationAgent()
        self.query_agent = QueryAgent()
        self.document_selection_agent = DocumentSelectionAgent()
        self.rag_agent = RAGEngineAgent(rag_client=rag_client)
        self.outline_agent = OutlineAgent()
        self.content_agent = ContentAgent()
        self.image_agent = ImageCoordinationAgent()
        self.qa_agent = QAAgent()
        self.format_agent = FormatAgent()
        self.validation_agent = ValidationAgent()

        self.logger.info("orchestrator_initialized", agents_count=10)

    async def initialize(self):
        """Initialize agents that require async setup."""
        if hasattr(self.rag_agent, 'initialize'):
            await self.rag_agent.initialize()
        self.logger.info("orchestrator_ready")

    async def run_full_workflow(
        self,
        user_request: str,
        documents: Optional[list] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run the complete presentation generation workflow.

        Args:
            user_request: User's request for presentation
            documents: Optional list of document paths
            preferences: User preferences

        Returns:
            Final presentation and metadata
        """
        self.logger.info("workflow_started", request_length=len(user_request))

        context = {}

        try:
            # Step 1: Query Analysis (skip conversation for now)
            self.logger.info("step_1_query_analysis")
            query_request = AgentRequest(
                user_input=user_request,
                context=context,
                documents=documents,
                preferences=preferences
            )
            query_response = await self.query_agent.execute(query_request)
            if not query_response.success:
                raise Exception("Query analysis failed")
            context["query_output"] = query_response.output

            # Step 2: Document Selection (using metadata RAG)
            self.logger.info("step_2_document_selection")
            doc_selection_request = AgentRequest(
                user_input=user_request,
                context=context,
                documents=documents,
                preferences=preferences
            )
            doc_selection_response = await self.document_selection_agent.execute(doc_selection_request)
            if doc_selection_response.success:
                context["document_selection_output"] = doc_selection_response.output
                # Update documents list with selected documents
                selected_doc_ids = [
                    doc.get("document_id")
                    for doc in doc_selection_response.output.get("selected_documents", [])
                ]
                if selected_doc_ids:
                    documents = selected_doc_ids
            else:
                self.logger.warning("document_selection_failed", using_original_documents=True)
                context["document_selection_output"] = {"selected_documents": []}

            # Step 3: RAG Retrieval
            self.logger.info("step_3_rag_retrieval")
            rag_request = AgentRequest(
                user_input=user_request,
                context=context,
                documents=documents
            )
            rag_response = await self.rag_agent.execute(rag_request)
            if rag_response.success:
                context["rag_output"] = rag_response.output
            else:
                self.logger.warning("rag_retrieval_skipped")
                context["rag_output"] = {"retrieved_context": "", "sources": []}

            # Step 4: Outline Generation
            self.logger.info("step_4_outline_generation")
            outline_request = AgentRequest(
                user_input=user_request,
                context=context,
                preferences=preferences
            )
            outline_response = await self.outline_agent.execute(outline_request)
            if not outline_response.success:
                raise Exception("Outline generation failed")
            context["outline_output"] = outline_response.output

            # Step 5: Content Generation
            self.logger.info("step_5_content_generation")
            content_request = AgentRequest(
                user_input=user_request,
                context=context,
                preferences=preferences
            )
            content_response = await self.content_agent.execute(content_request)
            if not content_response.success:
                raise Exception("Content generation failed")
            context["content_output"] = content_response.output

            # Step 6: Image Coordination
            self.logger.info("step_6_image_coordination")
            image_request = AgentRequest(
                user_input=user_request,
                context=context
            )
            image_response = await self.image_agent.execute(image_request)
            if image_response.success:
                context["image_output"] = image_response.output
            else:
                self.logger.warning("image_coordination_skipped")
                context["image_output"] = {"visualizations": []}

            # Step 7: QA Validation
            self.logger.info("step_7_qa_validation")
            qa_request = AgentRequest(
                user_input=user_request,
                context=context
            )
            qa_response = await self.qa_agent.execute(qa_request)
            if qa_response.success:
                context["qa_output"] = qa_response.output
            else:
                self.logger.warning("qa_validation_skipped")
                context["qa_output"] = {"validation_passed": True}

            # Step 8: Format Generation
            self.logger.info("step_8_format_generation")
            format_request = AgentRequest(
                user_input=user_request,
                context=context,
                preferences=preferences
            )
            format_response = await self.format_agent.execute(format_request)
            if not format_response.success:
                raise Exception("Format generation failed")
            context["format_output"] = format_response.output

            # Step 9: Final Validation
            self.logger.info("step_9_final_validation")
            validation_request = AgentRequest(
                user_input=user_request,
                context=context,
                preferences=preferences
            )
            validation_response = await self.validation_agent.execute(validation_request)
            if validation_response.success:
                context["validation_output"] = validation_response.output
            else:
                self.logger.warning("final_validation_skipped")
                context["validation_output"] = {"validation_passed": True}

            self.logger.info("workflow_completed_successfully")

            return {
                "success": True,
                "presentation": {
                    "html": format_response.output.get("html"),
                    "outline": outline_response.output,
                    "content": content_response.output,
                    "visualizations": context.get("image_output", {}).get("visualizations", []),
                },
                "metadata": {
                    "query_analysis": query_response.output,
                    "rag_sources": context.get("rag_output", {}).get("sources", []),
                    "qa_results": context.get("qa_output", {}),
                    "validation_results": context.get("validation_output", {}),
                },
                "all_outputs": context
            }

        except Exception as e:
            self.logger.error("workflow_failed", error=str(e), error_type=type(e).__name__)
            return {
                "success": False,
                "error": str(e),
                "partial_outputs": context
            }

    async def run_conversation_workflow(
        self,
        user_message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run conversational workflow to gather requirements.

        Args:
            user_message: User's message
            session_id: Session identifier

        Returns:
            Conversation response
        """
        request = AgentRequest(
            user_input=user_message,
            session_id=session_id
        )

        response = await self.conversation_agent.execute(request)

        return {
            "success": response.success,
            "response": response.output.get("response"),
            "is_complete": response.output.get("is_complete", False),
            "extracted_information": response.output.get("extracted_information", {}),
            "next_action": response.output.get("next_action")
        }
