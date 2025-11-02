"""Conversation Agent with dual-mode (Generation/Editing) and RBAC support."""
from typing import Any, Dict, List, Optional
import json
import structlog
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic

from src.agents.base import BaseAgent, AgentRequest, AgentType
from src.agents.config import get_agent_config
from .prompts import (
    CONVERSATION_SYSTEM_PROMPT,
    INFORMATION_EXTRACTION_PROMPT,
    EDIT_CLASSIFICATION_PROMPT,
    CLARIFICATION_PROMPT,
    CONFIRMATION_SUMMARY_PROMPT,
    REACT_AGENT_TEMPLATE,
    RBAC_VALIDATION_PROMPT,
)

logger = structlog.get_logger(__name__)


class ConversationAgent(BaseAgent):
    """Agent for conversational information gathering with dual-mode and RBAC support.

    Supports two operational modes:
    1. GENERATION MODE: Gather requirements for new presentation
    2. EDITING MODE: Process modification requests for existing presentation
    """

    def __init__(self):
        """Initialize Conversation Agent with dual-mode and RBAC setup."""
        config = get_agent_config(AgentType.CONVERSATION)
        super().__init__(
            agent_name="conversation_agent",
            agent_type=AgentType.CONVERSATION,
            config=config,
        )
        
        # Conversation state
        self.conversation_history: List[Dict[str, str]] = []
        self.extracted_info: Dict[str, Any] = {}
        self.conversation_state = "gathering"
        self.tool_call_count = 0
        
        # Mode tracking
        self.cycle_type = "generate"  # generation or editing
        
        # RBAC-related state
        self.user_profile: Optional[Dict[str, Any]] = None
        self.accessible_documents: List[Dict[str, Any]] = []
        self.rbac_warnings: List[str] = []
        self.out_of_scope_requests: List[str] = []
        self.suggested_documents: List[str] = []
        
        # Editing mode state
        self.editing_context: Optional[Dict[str, Any]] = None
        self.previous_presentation: Optional[Dict[str, Any]] = None
        
        # RBAC validation results
        self.rbac_validation: Dict[str, Any] = {
            "validation_result": "allowed",
            "allowed_items": [],
            "denied_items": [],
            "explanation": "",
            "suggested_alternatives": [],
            "professional_message": None
        }
        
        # Initialize LangChain components
        self._init_langchain_agent()
        
        self.logger.info(
            "conversation_agent_initialized",
            langchain_agent_type="CONVERSATIONAL_REACT_DESCRIPTION",
            has_memory=True,
            rbac_enabled=True,
            dual_mode=True,
        )

    def set_user_profile(self, user_profile: Dict[str, Any]):
        """Set user profile for RBAC."""
        self.user_profile = user_profile
        self.logger.info(
            "user_profile_set",
            user_id=user_profile.get("userId"),
            role=user_profile.get("role"),
            department=user_profile.get("department"),
            access_scopes=user_profile.get("accessScopes", [])
        )

    def set_accessible_documents(self, documents: List[Dict[str, Any]]):
        """Set accessible documents for user."""
        self.accessible_documents = documents
        self.logger.info(
            "accessible_documents_set",
            document_count=len(documents),
            departments=[doc.get("department") for doc in documents],
            doc_types=[doc.get("docType") for doc in documents]
        )

    def set_cycle_type(self, cycle_type: str):
        """Set operational mode (generation or editing)."""
        self.cycle_type = cycle_type
        self.logger.info("cycle_type_set", cycle_type=cycle_type)

    def set_editing_context(self, editing_context: Dict[str, Any]):
        """Set editing context for editing mode."""
        self.editing_context = editing_context
        if editing_context.get("isEditing"):
            self.previous_presentation = editing_context.get("previousResponse", {})
            self.cycle_type = "edit"
            self.conversation_state = "edit"
        self.logger.info(
            "editing_context_set",
            is_editing=editing_context.get("isEditing"),
            target_slide=editing_context.get("targetSlide"),
            edit_type=editing_context.get("editType")
        )

    def _init_langchain_agent(self):
        """Initialize LangChain agent with tools and memory."""
        self.llm = ChatAnthropic(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output",
        )
        
        # Create tools (includes mode-aware tools)
        self.tools = self._create_agent_tools()
        
        # Create ReAct prompt
        react_prompt = PromptTemplate(
            template=REACT_AGENT_TEMPLATE,
            input_variables=["input", "chat_history", "agent_scratchpad"],
            partial_variables={
                "cycle_type": self.cycle_type,
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools]),
            },
        )
        
        # Create agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=react_prompt,
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=6,  # Increased for editing mode
            max_execution_time=30,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def _create_agent_tools(self) -> List[Tool]:
        """Create tools for dual-mode conversation agent with RBAC."""
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
                name="classify_edit_request",
                func=self._tool_classify_edit,
                description=(
                    "EDITING MODE ONLY: Classify edit type and determine target agent. "
                    "Input: edit request text. "
                    "Returns: Edit classification with type, scope, target agent."
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
                name="suggest_accessible_documents",
                func=self._tool_suggest_documents,
                description=(
                    "GENERATION MODE: Suggest documents from user's accessible list. "
                    "Input: presentation requirements as JSON. "
                    "Returns: List of relevant accessible documents."
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
            Tool(
                name="create_confirmation_summary",
                func=self._tool_create_confirmation,
                description=(
                    "Create confirmation summary with next agent routing. "
                    "Input: 'create summary'. "
                    "Returns: Formatted confirmation with handoff details."
                ),
            ),
        ]
        return tools

    def _tool_extract_information(self, input_text: str = "") -> str:
        """Tool: Extract structured information with mode and RBAC awareness."""
        try:
            self.tool_call_count += 1
            
            # Build conversation history
            history_str = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in self.conversation_history[-6:]
            ])
            
            latest_message = self.conversation_history[-1]['content'] if self.conversation_history else ""
            
            # User context
            user_context = ""
            if self.user_profile:
                user_context = f"""
USER PROFILE:
- Name: {self.user_profile.get('name')}
- Role: {self.user_profile.get('role')}
- Department: {self.user_profile.get('department')}
- Access Scopes: {', '.join(self.user_profile.get('accessScopes', []))}
- Permissions: {json.dumps(self.user_profile.get('permissions', {}), indent=2)}
- Accessible Documents: {len(self.accessible_documents)} documents
"""
            
            # Editing context
            editing_context_str = ""
            if self.cycle_type == "edit" and self.editing_context:
                editing_context_str = f"""
EDITING CONTEXT:
- Target Slide: {self.editing_context.get('targetSlide')}
- Edit Type: {self.editing_context.get('editType')}
- Edit Query: {self.editing_context.get('editQuery')}
- Previous Presentation Available: {bool(self.previous_presentation)}
"""
            
            prompt = INFORMATION_EXTRACTION_PROMPT.format(
                cycle_type=self.cycle_type.upper(),
                user_context=user_context,
                conversation_history=history_str,
                user_message=latest_message,
                editing_context=editing_context_str,
            )
            
            response = self.llm.invoke(prompt)
            extracted = self._parse_json_response(response.content)
            
            # Store extracted info
            self.extracted_info = extracted
            
            self.logger.info(
                "information_extracted",
                cycle_type=self.cycle_type,
                is_complete=extracted.get("is_complete", False),
                confidence=extracted.get("confidence_score", 0),
                missing_count=len(extracted.get("missing_information", [])),
                rbac_concerns=len(extracted.get("rbac_concerns", []))
            )
            
            # Return simplified summary
            summary = {
                "cycle_type": self.cycle_type,
                "confidence": extracted.get("confidence_score", 0),
                "is_complete": extracted.get("is_complete", False),
                "conversation_state": extracted.get("conversation_state", "gathering"),
                "missing_count": len(extracted.get("missing_information", [])),
                "top_missing": extracted.get("missing_information", [])[:3],
                "rbac_concerns": extracted.get("rbac_concerns", []),
                "editing_requirements": extracted.get("editing_requirements"),
            }
            
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            self.logger.error("extraction_tool_failed", error=str(e))
            return json.dumps({"error": str(e), "is_complete": False})

    def _tool_classify_edit(self, edit_request: str) -> str:
        """Tool: Classify edit request (EDITING MODE only)."""
        try:
            self.tool_call_count += 1
            
            if self.cycle_type != "edit":
                return json.dumps({"error": "Not in editing mode"})
            
            # Previous context
            previous_context = ""
            if self.previous_presentation:
                previous_context = json.dumps(self.previous_presentation, indent=2)[:500]  # Limit size
            
            prompt = EDIT_CLASSIFICATION_PROMPT.format(
                edit_request=edit_request,
                previous_context=previous_context,
                user_role=self.user_profile.get("role", "unknown"),
                user_department=self.user_profile.get("department", "unknown"),
                access_scopes=", ".join(self.user_profile.get("accessScopes", [])),
            )
            
            response = self.llm.invoke(prompt)
            classification = self._parse_json_response(response.content)
            
            # Store in extracted_info
            if "editing_requirements" not in self.extracted_info:
                self.extracted_info["editing_requirements"] = {}
            
            self.extracted_info["editing_requirements"].update({
                "edit_type": classification.get("edit_type"),
                "edit_scope": classification.get("edit_scope"),
                "target_slide": classification.get("target_slide"),
                "specific_changes": classification.get("specific_changes", []),
            })
            
            self.logger.info(
                "edit_classified",
                edit_type=classification.get("edit_type"),
                target_agent=classification.get("target_agent"),
                requires_clarification=classification.get("requires_clarification")
            )
            
            return json.dumps(classification, indent=2)
            
        except Exception as e:
            self.logger.error("edit_classification_failed", error=str(e))
            return json.dumps({"error": str(e), "edit_type": "general"})

    def _tool_validate_rbac(self, request_json: str) -> str:
        """Tool: Validate RBAC for requested data."""
        try:
            self.tool_call_count += 1
            
            if not self.user_profile:
                return json.dumps({"error": "No user profile set"})
            
            requested_items = json.loads(request_json) if isinstance(request_json, str) else request_json
            
            access_scopes = self.user_profile.get("accessScopes", [])
            permissions = self.user_profile.get("permissions", {})
            
            prompt = RBAC_VALIDATION_PROMPT.format(
                user_role=self.user_profile.get("role"),
                user_department=self.user_profile.get("department"),
                access_scopes=", ".join(access_scopes),
                permissions=json.dumps(permissions, indent=2),
                requested_items=json.dumps(requested_items, indent=2),
                cycle_type=self.cycle_type.upper(),
            )
            
            response = self.llm.invoke(prompt)
            validation = self._parse_json_response(response.content)
            
            # Store RBAC validation
            self.rbac_validation = validation
            
            # Store warnings
            if validation.get("denied_items"):
                warning_msg = validation.get("professional_message", 
                    f"Some requested data is outside your access scope: {', '.join(validation['denied_items'])}")
                self.rbac_warnings.append(warning_msg)
                self.out_of_scope_requests.extend(validation["denied_items"])
            
            self.logger.info(
                "rbac_validated",
                validation_result=validation.get("validation_result"),
                allowed_count=len(validation.get("allowed_items", [])),
                denied_count=len(validation.get("denied_items", [])),
                user_role=self.user_profile.get("role")
            )
            
            return json.dumps(validation, indent=2)
            
        except Exception as e:
            self.logger.error("rbac_validation_failed", error=str(e))
            return json.dumps({
                "error": str(e),
                "validation_result": "allowed",
                "allowed_items": [],
                "denied_items": []
            })

    def _tool_suggest_documents(self, requirements_json: str) -> str:
        """Tool: Suggest accessible documents (GENERATION MODE)."""
        try:
            self.tool_call_count += 1
            
            if self.cycle_type != "generate":
                return json.dumps({"suggested_documents": []})
            
            requirements = json.loads(requirements_json) if isinstance(requirements_json, str) else requirements_json
            
            # Score documents
            scored_docs = []
            
            topic = requirements.get("presentation_requirements", {}).get("topic", "").lower()
            themes = [t.lower() for t in requirements.get("presentation_requirements", {}).get("key_themes", [])]
            content_needs = [c.lower() for c in requirements.get("data_requirements", {}).get("content_to_extract", [])]
            
            for doc in self.accessible_documents:
                score = 0
                reasons = []
                
                # Topic match
                if topic and topic in doc.get("summary", "").lower():
                    score += 3
                    reasons.append("topic match")
                
                # Theme overlap
                doc_topics = [t.lower() for t in doc.get("topics", [])]
                theme_overlap = len(set(themes) & set(doc_topics))
                if theme_overlap > 0:
                    score += theme_overlap * 2
                    reasons.append(f"{theme_overlap} theme matches")
                
                # Content needs in tags
                doc_tags = [t.lower() for t in doc.get("tags", [])]
                content_overlap = len(set(content_needs) & set(doc_tags))
                if content_overlap > 0:
                    score += content_overlap
                    reasons.append(f"{content_overlap} content matches")
                
                if score > 0:
                    scored_docs.append({
                        "document_id": doc.get("documentId"),
                        "document_name": doc.get("documentName"),
                        "doc_type": doc.get("docType"),
                        "department": doc.get("department"),
                        "relevance_score": score,
                        "match_reasons": reasons,
                    })
            
            # Sort and take top 5
            scored_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
            suggested = scored_docs[:5]
            
            # Update state
            self.suggested_documents = [doc["document_name"] for doc in suggested]
            
            self.logger.info(
                "documents_suggested",
                suggested_count=len(suggested),
                total_accessible=len(self.accessible_documents)
            )
            
            return json.dumps({"suggested_documents": suggested}, indent=2)
            
        except Exception as e:
            self.logger.error("document_suggestion_failed", error=str(e))
            return json.dumps({"suggested_documents": []})

    def _tool_generate_followup(self, input_text: str = "") -> str:
        """Tool: Generate follow-up question (mode-aware)."""
        try:
            self.tool_call_count += 1
            
            # User context
            user_context = ""
            user_name = "there"
            user_department = "your department"
            
            if self.user_profile:
                user_name = self.user_profile.get('name', '').split()[0] if self.user_profile.get('name') else "there"
                user_department = self.user_profile.get('department', 'your department')
                user_context = f"""
    USER CONTEXT:
    - Name: {self.user_profile.get('name')}
    - Role: {self.user_profile.get('role')}
    - Department: {user_department}
    """
            
            # Mode-specific logic
            if self.cycle_type == "generate":
                missing_info = self.extracted_info.get("missing_information", [])
                if not missing_info:
                    return "Could you tell me more about your presentation needs?"
                
                top_missing = missing_info[0]
                clarification_needed = ""
            else:  # editing mode
                editing_reqs = self.extracted_info.get("editing_requirements", {})
                top_missing = ""
                clarification_needed = editing_reqs.get("specific_changes", ["unclear edit"])[0]
            
            # Prepare accessible documents list
            accessible_doc_list = [doc.get("documentName") for doc in self.accessible_documents]
            document_names = ", ".join(accessible_doc_list) if accessible_doc_list else "your documents"
            
            # For editing mode - extract additional context
            slide_number = ""
            edit_request = ""
            restricted_data = "certain data"
            alternative_data = "accessible alternatives"
            
            if self.cycle_type == "edit" and self.editing_context:
                slide_number = str(self.editing_context.get("targetSlide", ""))
                edit_request = self.editing_context.get("editQuery", "")
                
                # Check for RBAC issues
                if self.rbac_validation.get("denied_items"):
                    restricted_data = ", ".join(self.rbac_validation["denied_items"][:2])
                    if self.rbac_validation.get("suggested_alternatives"):
                        alternative_data = ", ".join(self.rbac_validation["suggested_alternatives"][:2])
            
            # Build the prompt with ALL required variables
            prompt = CLARIFICATION_PROMPT.format(
                cycle_type=self.cycle_type.upper(),
                user_context=user_context,
                current_requirements=json.dumps(
                    self.extracted_info.get("presentation_requirements", {}), indent=2
                ),
                missing_info=top_missing,
                clarification_needed=clarification_needed,
                accessible_documents=accessible_doc_list,
                name=user_name,
                department=user_department,
                document_names=document_names,
                slide_number=slide_number,
                edit_request=edit_request,
                restricted_data=restricted_data,
                alternative_data=alternative_data,
            )
            
            response = self.llm.invoke(prompt)
            question = response.content.strip()
            question = question.replace("```", "").replace("**", "").strip()
            
            self.logger.info(
                "followup_generated",
                cycle_type=self.cycle_type,
                missing_item=top_missing or "edit_clarification",
                user_name=user_name
            )
            
            return question
            
        except Exception as e:
            self.logger.error("followup_tool_failed", error=str(e))
            return "Could you provide more details?"

    def _tool_create_confirmation(self, input_text: str = "") -> str:
        """Tool: Create confirmation summary (mode-aware)."""
        try:
            self.tool_call_count += 1
            
            # RBAC context
            rbac_context = ""
            if self.rbac_warnings:
                rbac_context = f"""
RBAC STATUS:
- Warnings: {len(self.rbac_warnings)}
- Out-of-scope requests: {len(self.out_of_scope_requests)}
- Validation result: {self.rbac_validation.get('validation_result')}
- Professional message: {self.rbac_validation.get('professional_message')}
"""
            
            prompt = CONFIRMATION_SUMMARY_PROMPT.format(
                cycle_type=self.cycle_type.upper(),
                extracted_info=json.dumps(self.extracted_info, indent=2),
                rbac_context=rbac_context,
                suggested_documents=", ".join(self.suggested_documents) if self.suggested_documents else "None",
            )
            
            response = self.llm.invoke(prompt)
            confirmation = response.content.strip()
            
            self.logger.info(
                "confirmation_summary_created",
                cycle_type=self.cycle_type
            )
            
            return confirmation
            
        except Exception as e:
            self.logger.error("confirmation_tool_failed", error=str(e))
            return self._create_basic_confirmation(self.extracted_info)

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute conversation agent logic with dual-mode support."""
        user_input = request.user_input
        context = request.context or {}
        
        # Reset tool call counter
        self.tool_call_count = 0
        
        # Extract mode and editing context from request
        self.cycle_type = context.get("cycleType", "generate")
        
        if "editingContext" in context:
            self.set_editing_context(context["editingContext"])
        
        # Personalized greeting for first message in generation mode
        if not self.conversation_history and self.user_profile and self.cycle_type == "generate":
            user_name = self.user_profile.get("name", "").split()[0]
            user_role = self.user_profile.get("role", "").replace("_", " ").title()
            greeting = f"\n[System: Greet {user_name}, a {user_role} in {self.user_profile.get('department')} department. They have access to {len(self.accessible_documents)} documents. MODE: {self.cycle_type.upper()}]"
            user_input = greeting + "\n\nUser: " + user_input
        
        # Update conversation history
        self.conversation_history.append({
            "role": "user",
            "content": request.user_input,
            "timestamp": datetime.utcnow().isoformat(),
            "cycle_type": self.cycle_type,
        })
        
        try:
            # Execute agent
            result = await self._execute_langchain_agent(user_input, context)
            
            response_text = result.get("output", "")
            
            if not response_text or response_text.strip() == "":
                response_text = await self._generate_fallback_response()
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            # Post-process: Force completion if all fields filled and user confirmed
            if self.cycle_type == "generate":
                user_input_lower = request.user_input.lower()
                
                # Check for confirmation keywords
                confirmation_keywords = [
                    "proceed", "let's go", "lets go", "start", "create", "yes", "confirmed",
                    "go ahead", "that works", "perfect", "sounds good", "let's do it", "lets do it",
                    "begin", "yep", "sure", "okay", "ok", "looks good", "that's good", "thats good",
                    "create it", "make it", "do it", "go for it", "approved", "confirm"
                ]
                
                user_confirmed = any(keyword in user_input_lower for keyword in confirmation_keywords)
                
                if user_confirmed:
                    reqs = self.extracted_info.get("presentation_requirements", {})
                    data_reqs = self.extracted_info.get("data_requirements", {})
                    visual_prefs = self.extracted_info.get("visual_preferences", {})
                    
                    # Check all 8 critical fields
                    topic_filled = bool(reqs.get("topic"))
                    audience_filled = bool(reqs.get("target_audience"))
                    objectives_filled = bool(reqs.get("objectives"))
                    themes_filled = len(reqs.get("key_themes", [])) >= 2
                    content_filled = len(data_reqs.get("content_to_extract", [])) >= 1
                    visual_filled = (len(visual_prefs.get("chart_types", [])) >= 1 or bool(visual_prefs.get("style")))
                    tone_filled = bool(reqs.get("tone"))
                    slides_filled = bool(reqs.get("num_slides"))
                    
                    all_filled = (
                        topic_filled and
                        audience_filled and
                        objectives_filled and
                        themes_filled and
                        content_filled and
                        visual_filled and
                        tone_filled and
                        slides_filled
                    )
                    
                    if all_filled:
                        # Force completion
                        self.extracted_info["is_complete"] = True
                        self.extracted_info["confidence_score"] = 1.0
                        self.extracted_info["conversation_state"] = "complete"
                        self.extracted_info["missing_information"] = []
                        
                        self.logger.info(
                            "forced_completion_on_confirmation",
                            user_confirmed=user_confirmed,
                            all_fields_filled=all_filled,
                            topic=topic_filled,
                            audience=audience_filled,
                            objectives=objectives_filled,
                            themes=themes_filled,
                            content=content_filled,
                            visual=visual_filled,
                            tone=tone_filled,
                            slides=slides_filled
                        )
                    else:
                        # Log which fields are missing
                        missing_fields = []
                        if not topic_filled: missing_fields.append("topic")
                        if not audience_filled: missing_fields.append("target_audience")
                        if not objectives_filled: missing_fields.append("objectives")
                        if not themes_filled: missing_fields.append("key_themes")
                        if not content_filled: missing_fields.append("content_to_extract")
                        if not visual_filled: missing_fields.append("visual_preferences")
                        if not tone_filled: missing_fields.append("tone")
                        if not slides_filled: missing_fields.append("num_slides")
                        
                        self.logger.warning(
                            "confirmation_received_but_fields_incomplete",
                            user_confirmed=user_confirmed,
                            missing_fields=missing_fields,
                            current_confidence=self.extracted_info.get("confidence_score", 0)
                        )
            
            # Determine state and next action
            is_complete = self.extracted_info.get("is_complete", False)
            confidence = self.extracted_info.get("confidence_score", 0)
            conversation_state = self.extracted_info.get("conversation_state", "gathering")
            
            # Determine next action based on mode
            if self.cycle_type == "edit":
                if is_complete:
                    editing_reqs = self.extracted_info.get("editing_requirements", {})
                    edit_type = editing_reqs.get("edit_type", "general")
                    
                    # Determine handoff agent
                    if edit_type == "content":
                        next_action = "handoff_to_content_agent"
                        handoff_agent = "Content Agent"
                    elif edit_type == "visual":
                        next_action = "handoff_to_image_agent"
                        handoff_agent = "Image Coordination Agent"
                    elif edit_type == "structure":
                        next_action = "handoff_to_outline_agent"
                        handoff_agent = "Outline Agent"
                    else:
                        next_action = "request_clarification"
                        handoff_agent = None
                else:
                    next_action = "request_clarification"
                    handoff_agent = None
            else:  # generation mode
                if is_complete:
                    next_action = "handoff_to_document_selection"
                    handoff_agent = "Document Selection Agent"
                else:
                    next_action = "continue_conversation"
                    handoff_agent = None
            
            return {
                "response": response_text,
                "is_complete": is_complete,
                "extracted_information": self.extracted_info,
                "rbac_validation": self.rbac_validation,
                "rbac_concerns": self.extracted_info.get("rbac_concerns", []),
                "missing_information": self.extracted_info.get("missing_information", []),
                "confidence_score": confidence,
                "conversation_state": conversation_state,
                "next_action": next_action,
                "handoff_to_agent": handoff_agent,
                "rbac_warnings": self.rbac_warnings,
                "suggested_documents": self.suggested_documents,
                "conversation_history": self.conversation_history,
                "tool_calls_made": self.tool_call_count,
                "cycle_type": self.cycle_type,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            self.logger.error("agent_execution_failed", error=str(e))
            fallback_response = "I apologize, but I encountered an issue. Could you please rephrase that?"
            
            self.conversation_history.append({
                "role": "assistant",
                "content": fallback_response,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            return {
                "response": fallback_response,
                "is_complete": False,
                "extracted_information": self.extracted_info,
                "rbac_validation": self.rbac_validation,
                "conversation_history": self.conversation_history,
                "next_action": "continue_conversation",
                "error": str(e),
                "rbac_warnings": self.rbac_warnings,
            }

    async def _execute_langchain_agent(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the LangChain agent."""
        try:
            result = self.agent_executor.invoke({"input": user_input})
            response_text = result.get("output", "")
            
            self.logger.info(
                "langchain_agent_executed",
                cycle_type=self.cycle_type,
                tool_calls=self.tool_call_count,
                has_output=bool(response_text),
            )
            
            return {"output": response_text, "full_result": result}
            
        except Exception as e:
            self.logger.error("langchain_agent_error", error=str(e))
            raise

    async def _generate_fallback_response(self) -> str:
        """Generate fallback response."""
        if self.cycle_type == "edit":
            return "Could you clarify what changes you'd like to make?"
        
        if not self.extracted_info and self.user_profile:
            user_name = self.user_profile.get("name", "").split()[0]
            return f"Hi {user_name}! I'm here to help you create a presentation. What would you like to present?"
        
        missing = self.extracted_info.get("missing_information", [])
        if missing:
            return f"Could you tell me more about {missing[0].replace('_', ' ')}?"
        
        return "Thanks! Could you tell me a bit more?"

    def _create_basic_confirmation(self, extracted_info: Dict[str, Any]) -> str:
        """Create basic confirmation (fallback)."""
        if self.cycle_type == "edit":
            editing_reqs = extracted_info.get("editing_requirements", {})
            parts = ["Got it! I'll make these changes:"]
            
            if editing_reqs.get("target_slide"):
                parts.append(f"• Target: Slide {editing_reqs['target_slide']}")
            if editing_reqs.get("specific_changes"):
                parts.append(f"• Changes: {', '.join(editing_reqs['specific_changes'][:2])}")
            
            parts.append("\nProceed with these updates?")
            return "\n".join(parts)
        
        # Generation mode
        reqs = extracted_info.get("presentation_requirements", {})
        parts = []
        
        if self.user_profile:
            user_name = self.user_profile.get("name", "").split()[0]
            parts.append(f"Great, {user_name}! Here's what I have:")
        else:
            parts.append("Great! Here's what I have:")
        
        if reqs.get("topic"):
            parts.append(f"• Topic: {reqs['topic']}")
        if reqs.get("target_audience"):
            parts.append(f"• Audience: {reqs['target_audience']}")
        if self.suggested_documents:
            parts.append(f"• Documents: {', '.join(self.suggested_documents[:3])}")
        
        if self.rbac_warnings:
            parts.append("\n⚠️  Note: Some requested data may be outside your access scope.")
        
        parts.append("\nShall I proceed?")
        return "\n".join(parts)

    def reset_conversation(self):
        """Reset conversation state."""
        self.conversation_history = []
        self.extracted_info = {}
        self.conversation_state = "gathering"
        self.tool_call_count = 0
        self.cycle_type = "generate"
        self.rbac_warnings = []
        self.out_of_scope_requests = []
        self.suggested_documents = []
        self.editing_context = None
        self.previous_presentation = None
        self.rbac_validation = {
            "validation_result": "allowed",
            "allowed_items": [],
            "denied_items": [],
            "explanation": "",
            "suggested_alternatives": [],
            "professional_message": None
        }
        self.memory.clear()
        self.logger.info("conversation_reset")

    def get_requirements_for_next_agent(self) -> Dict[str, Any]:
        """Get formatted requirements for next agent (mode-aware)."""
        base_output = {
            "cycle_type": self.cycle_type,
            "requirements": self.extracted_info,
            "conversation_history": self.conversation_history,
            "user_profile": self.user_profile,
            "accessible_documents": self.accessible_documents,
            "rbac_validation": self.rbac_validation,
            "rbac_warnings": self.rbac_warnings,
            "session_metadata": {
                "total_turns": len(self.conversation_history) // 2,
                "confidence_score": self.extracted_info.get("confidence_score", 0),
                "completed_at": datetime.utcnow().isoformat(),
            },
        }
        
        if self.cycle_type == "generate":
            base_output["suggested_documents"] = self.suggested_documents
        else:
            base_output["editing_context"] = self.editing_context
            base_output["previous_presentation"] = self.previous_presentation
        
        return base_output