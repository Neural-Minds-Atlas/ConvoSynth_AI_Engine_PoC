"""Conversation Agent adapted for MongoDB backend."""
from typing import Any, Dict, List, Optional
import json
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate

from app.config import settings
from app.db.models import (
    UserProfile,
    AccessibleDocument,
    ConversationMessage,
    ExtractedInformation,
    RBACValidation,
)
from app.db.repositories import ConversationRepository, DocumentRepository
from app.services.rbac_service import RBACService
from app.services.llm_service import LLMService
from app.utils.logger import get_logger
from app.utils.security import generate_session_id
from app.utils.exceptions import AgentException
from .prompts import (
    CONVERSATION_SYSTEM_PROMPT,
    INFORMATION_EXTRACTION_PROMPT,
    EDIT_CLASSIFICATION_PROMPT,
    CLARIFICATION_PROMPT,
    CONFIRMATION_SUMMARY_PROMPT,
    REACT_AGENT_TEMPLATE,
    RBAC_VALIDATION_PROMPT,
)

logger = get_logger(__name__)


class ConversationAgent:
    """Conversation Agent with dual-mode and RBAC support."""

    def __init__(
        self,
        llm_service: LLMService,
        rbac_service: RBACService,
        conversation_repo: ConversationRepository,
        document_repo: DocumentRepository,
    ):
        """Initialize Conversation Agent.

        Args:
            llm_service: LLM service instance
            rbac_service: RBAC service instance
            conversation_repo: Conversation repository
            document_repo: Document repository
        """
        self.llm = llm_service.get_llm_instance()
        self.llm_service = llm_service
        self.rbac_service = rbac_service
        self.conversation_repo = conversation_repo
        self.document_repo = document_repo

        # Agent state (per-request)
        self.user_profile: Optional[UserProfile] = None
        self.accessible_documents: List[AccessibleDocument] = []
        self.cycle_type = "generation"
        self.extracted_info: Dict[str, Any] = {}
        self.rbac_validation: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, str]] = []
        self.tool_call_count = 0

        logger.info("conversation_agent_initialized")

    def set_context(
        self,
        user_profile: UserProfile,
        accessible_documents: List[AccessibleDocument],
        cycle_type: str = "generation",
        conversation_history: List[Dict[str, str]] = None,
    ):
        """Set context for conversation.

        Args:
            user_profile: User profile
            accessible_documents: Accessible documents list
            cycle_type: generation or editing
            conversation_history: Previous conversation history
        """
        self.user_profile = user_profile
        self.accessible_documents = accessible_documents
        self.cycle_type = cycle_type
        self.conversation_history = conversation_history or []

        logger.info(
            "agent_context_set",
            user_id=user_profile.name,
            cycle_type=cycle_type,
            accessible_docs_count=len(accessible_documents),
        )

    async def process_message(
        self,
        user_message: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a user message.

        Args:
            user_message: User's input message
            session_id: Optional session ID

        Returns:
            Agent response dictionary
        """
        self.tool_call_count = 0

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat(),
        })

        try:
            # Initialize LangChain components
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="output",
            )

            # Create tools
            tools = self._create_agent_tools()

            # Create ReAct prompt
            react_prompt = PromptTemplate(
                template=REACT_AGENT_TEMPLATE,
                input_variables=["input", "chat_history", "agent_scratchpad"],
                partial_variables={
                    "cycle_type": self.cycle_type,
                    "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
                    "tool_names": ", ".join([tool.name for tool in tools]),
                },
            )

            # Create agent
            agent = create_react_agent(
                llm=self.llm,
                tools=tools,
                prompt=react_prompt,
            )

            # Create executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                memory=memory,
                verbose=settings.debug,
                max_iterations=settings.conversation_agent_max_iterations,
                max_execution_time=settings.conversation_agent_max_execution_time,
                handle_parsing_errors=True,
                return_intermediate_steps=True,
            )

            # Execute agent
            result = await agent_executor.ainvoke({"input": user_message})
            response_text = result.get("output", "")

            # Fallback response
            if not response_text or response_text.strip() == "":
                response_text = await self._generate_fallback_response()

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat(),
            })

            # Check for completion (generation mode)
            if self.cycle_type == "generation":
                self._check_completion_on_confirmation(user_message)

            # Determine state and next action
            is_complete = self.extracted_info.get("is_complete", False)
            confidence = self.extracted_info.get("confidence_score", 0)
            conversation_state = self.extracted_info.get("conversation_state", "gathering")

            # Determine next action and handoff
            next_action, handoff_agent = self._determine_next_action(is_complete)

            return {
                "response": response_text,
                "isComplete": is_complete,
                "extractedInformation": self.extracted_info,
                "rbacValidation": self.rbac_validation,
                "rbacConcerns": self.extracted_info.get("rbac_concerns", []),
                "missingInformation": self.extracted_info.get("missing_information", []),
                "rbacWarnings": self.rbac_validation.get("rbac_warnings", []),
                "suggestedDocuments": self.extracted_info.get("suggested_documents", []),
                "confidenceScore": confidence,
                "conversationState": conversation_state,
                "nextAction": next_action,
                "handoffToAgent": handoff_agent,
                "conversationHistory": self.conversation_history,
                "toolCallsMade": self.tool_call_count,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error("agent_execution_failed", error=str(e))
            fallback_response = "I apologize, but I encountered an issue. Could you please rephrase that?"

            self.conversation_history.append({
                "role": "assistant",
                "content": fallback_response,
                "timestamp": datetime.utcnow().isoformat(),
            })

            return {
                "response": fallback_response,
                "isComplete": False,
                "extractedInformation": self.extracted_info,
                "rbacValidation": self.rbac_validation,
                "rbacConcerns": [],
                "missingInformation": [],
                "rbacWarnings": [],
                "suggestedDocuments": [],
                "confidenceScore": 0.0,
                "conversationState": "error",
                "conversationHistory": self.conversation_history,
                "nextAction": "continue_conversation",
                "handoffToAgent": None,
                "toolCallsMade": self.tool_call_count,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    def _create_agent_tools(self) -> List[Tool]:
        """Create LangChain tools for the agent."""
        tools = [
            Tool(
                name="extract_information",
                func=self._tool_extract_information,
                description=(
                    "Extract requirements (Generation) or edit details (Editing) with RBAC awareness. "
                    "Use ONCE per turn. Input: empty string. "
                    "Returns: JSON with requirements/edits, missing info, RBAC status."
                ),
            ),
            Tool(
                name="validate_rbac_request",
                func=self._tool_validate_rbac,
                description=(
                    "Validate if user's request is within their access scope. "
                    "Input: JSON with requested data/metrics. "
                    "Returns: Validation result with allowed/denied items."
                ),
            ),
            Tool(
                name="generate_followup_question",
                func=self._tool_generate_followup,
                description=(
                    "Generate ONE follow-up question for missing info or edit clarification. "
                    "Input: 'next question' or 'clarify edit'. "
                    "Returns: A single conversational question."
                ),
            ),
        ]
        return tools

    def _tool_extract_information(self, input_text: str = "") -> str:
        """Extract structured information from conversation."""
        try:
            self.tool_call_count += 1

            history_str = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in self.conversation_history[-6:]
            ])

            latest_message = self.conversation_history[-1]['content'] if self.conversation_history else ""

            user_context = ""
            if self.user_profile:
                user_context = f"""
USER PROFILE:
- Name: {self.user_profile.name}
- Role: {self.user_profile.role}
- Department: {self.user_profile.department}
- Access Scopes: {', '.join(self.user_profile.accessScopes)}
"""

            prompt = INFORMATION_EXTRACTION_PROMPT.format(
                cycle_type=self.cycle_type.upper(),
                user_context=user_context,
                conversation_history=history_str,
                user_message=latest_message,
                editing_context="",
            )

            response = self.llm.invoke(prompt)
            extracted = self._parse_json_response(response.content)

            self.extracted_info = extracted

            logger.info(
                "information_extracted",
                cycle_type=self.cycle_type,
                is_complete=extracted.get("is_complete", False),
                confidence=extracted.get("confidence_score", 0),
            )

            summary = {
                "cycle_type": self.cycle_type,
                "confidence": extracted.get("confidence_score", 0),
                "is_complete": extracted.get("is_complete", False),
                "missing_count": len(extracted.get("missing_information", [])),
            }

            return json.dumps(summary, indent=2)

        except Exception as e:
            logger.error("extraction_tool_failed", error=str(e))
            return json.dumps({"error": str(e), "is_complete": False})

    def _tool_validate_rbac(self, request_json: str) -> str:
        """Validate RBAC for requested data."""
        try:
            self.tool_call_count += 1

            if not self.user_profile:
                return json.dumps({"error": "No user profile set"})

            requested_items = json.loads(request_json) if isinstance(request_json, str) else request_json

            prompt = RBAC_VALIDATION_PROMPT.format(
                user_role=self.user_profile.role,
                user_department=self.user_profile.department,
                access_scopes=", ".join(self.user_profile.accessScopes),
                permissions=json.dumps(self.user_profile.permissions.model_dump(), indent=2),
                requested_items=json.dumps(requested_items, indent=2),
                cycle_type=self.cycle_type.upper(),
            )

            response = self.llm.invoke(prompt)
            validation = self._parse_json_response(response.content)

            self.rbac_validation = validation

            logger.info(
                "rbac_validated",
                validation_result=validation.get("validation_result"),
                allowed_count=len(validation.get("allowed_items", [])),
                denied_count=len(validation.get("denied_items", [])),
            )

            return json.dumps(validation, indent=2)

        except Exception as e:
            logger.error("rbac_validation_failed", error=str(e))
            return json.dumps({
                "error": str(e),
                "validation_result": "allowed",
            })

    def _tool_generate_followup(self, input_text: str = "") -> str:
        """Generate follow-up question."""
        try:
            self.tool_call_count += 1

            user_name = self.user_profile.name.split()[0] if self.user_profile else "there"
            missing_info = self.extracted_info.get("missing_information", [])
            top_missing = missing_info[0] if missing_info else ""

            prompt = CLARIFICATION_PROMPT.format(
                cycle_type=self.cycle_type.upper(),
                user_context="",
                current_requirements=json.dumps(self.extracted_info.get("presentation_requirements", {})),
                missing_info=top_missing,
                clarification_needed="",
                accessible_documents=[doc.documentName for doc in self.accessible_documents],
                name=user_name,
                department=self.user_profile.department if self.user_profile else "",
                document_names=", ".join([doc.documentName for doc in self.accessible_documents]),
                slide_number="",
                edit_request="",
                restricted_data="",
                alternative_data="",
            )

            response = self.llm.invoke(prompt)
            question = response.content.strip()

            logger.info("followup_generated", cycle_type=self.cycle_type)

            return question

        except Exception as e:
            logger.error("followup_tool_failed", error=str(e))
            return "Could you provide more details?"

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from LLM."""
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            return json.loads(json_str)
        except Exception as e:
            logger.error("json_parse_failed", error=str(e), content_preview=content[:200])
            return {}

    async def _generate_fallback_response(self) -> str:
        """Generate fallback response."""
        if self.cycle_type == "editing":
            return "Could you clarify what changes you'd like to make?"

        if self.user_profile:
            user_name = self.user_profile.name.split()[0]
            return f"Hi {user_name}! I'm here to help you create a presentation. What would you like to present?"

        return "Thanks! Could you tell me a bit more?"

    def _check_completion_on_confirmation(self, user_message: str):
        """Check if user confirmed and all fields are filled."""
        user_input_lower = user_message.lower()

        confirmation_keywords = [
            "proceed", "let's go", "lets go", "start", "create", "yes", "confirmed",
            "go ahead", "that works", "perfect", "sounds good"
        ]

        user_confirmed = any(keyword in user_input_lower for keyword in confirmation_keywords)

        if user_confirmed:
            reqs = self.extracted_info.get("presentation_requirements", {})
            data_reqs = self.extracted_info.get("data_requirements", {})
            visual_prefs = self.extracted_info.get("visual_preferences", {})

            all_filled = (
                bool(reqs.get("topic")) and
                bool(reqs.get("target_audience")) and
                bool(reqs.get("objectives")) and
                len(reqs.get("key_themes", [])) >= 2 and
                len(data_reqs.get("content_to_extract", [])) >= 1 and
                (len(visual_prefs.get("chart_types", [])) >= 1 or bool(visual_prefs.get("style"))) and
                bool(reqs.get("tone")) and
                bool(reqs.get("num_slides"))
            )

            if all_filled:
                self.extracted_info["is_complete"] = True
                self.extracted_info["confidence_score"] = 1.0
                self.extracted_info["conversation_state"] = "complete"
                self.extracted_info["missing_information"] = []

                logger.info("forced_completion_on_confirmation", all_fields_filled=True)

    def _determine_next_action(self, is_complete: bool) -> tuple:
        """Determine next action and handoff agent."""
        if self.cycle_type == "editing":
            if is_complete:
                editing_reqs = self.extracted_info.get("editing_requirements", {})
                edit_type = editing_reqs.get("edit_type", "general")

                if edit_type == "content":
                    return "handoff_to_content_agent", "Content Agent"
                elif edit_type == "visual":
                    return "handoff_to_image_agent", "Image Coordination Agent"
                elif edit_type == "structure":
                    return "handoff_to_outline_agent", "Outline Agent"
                else:
                    return "request_clarification", None
            else:
                return "request_clarification", None
        else:  # generation mode
            if is_complete:
                return "handoff_to_document_selection", "Document Selection Agent"
            else:
                return "continue_conversation", None
