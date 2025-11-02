"""API routes for multi-agent system with separate generation and editing endpoints."""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Request, Body
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import structlog

from src.agents import ConversationAgent, AgentOrchestrator
from src.agents.base import AgentRequest
from src.db.mongodb import get_collection
from src.db.models import ConversationDocument, ConversationMessage

logger = structlog.get_logger(__name__)

router = APIRouter()

# In-memory session storage (replace with Redis/DB in production)
conversation_sessions: Dict[str, ConversationAgent] = {}


# Enums
class EditType(str, Enum):
    """Type of edit request."""
    CONTENT = "content"
    VISUAL = "visual"
    STRUCTURE = "structure"
    GENERAL = "general"


class EditScope(str, Enum):
    """Scope of edit operation."""
    SINGLE_SLIDE_CONTENT = "single_slide_content"
    MULTIPLE_SLIDES_CONTENT = "multiple_slides_content"
    ENTIRE_PRESENTATION_CONTENT = "entire_presentation_content"


class ValidationResult(str, Enum):
    """RBAC validation result."""
    ALLOWED = "allowed"
    PARTIALLY_ALLOWED = "partially_allowed"
    DENIED = "denied"


# Shared Models
class UserPermissions(BaseModel):
    """User permissions model."""
    view_financial_data: bool = Field(default=False, alias="viewFinancialData")
    view_operational_data: bool = Field(default=True, alias="viewOperationalData")
    view_hr_data: bool = Field(default=False, alias="viewHRData")
    view_sales_data: bool = Field(default=False, alias="viewSalesData")
    view_confidential_data: bool = Field(default=False, alias="viewConfidentialData")
    export_reports: bool = Field(default=True, alias="exportReports")

    class Config:
        populate_by_name = True


class UserProfile(BaseModel):
    """User profile with RBAC information."""
    user_id: str = Field(..., alias="userId")
    name: str
    role: str
    department: str
    access_scopes: List[str] = Field(..., alias="accessScopes")
    permissions: UserPermissions

    class Config:
        populate_by_name = True


class DocumentAccess(BaseModel):
    """Document access information with metadata."""
    document_id: str = Field(..., alias="documentId")
    document_name: str = Field(..., alias="documentName")
    doc_type: str = Field(..., alias="docType")
    department: str
    access_level: str = Field(..., alias="accessLevel")
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class RBACValidation(BaseModel):
    """RBAC validation result."""
    validation_result: ValidationResult = Field(..., alias="validationResult")
    allowed_items: List[str] = Field(default_factory=list, alias="allowedItems")
    denied_items: List[str] = Field(default_factory=list, alias="deniedItems")
    explanation: str
    suggested_alternatives: List[str] = Field(default_factory=list, alias="suggestedAlternatives")
    professional_message: Optional[str] = Field(default=None, alias="professionalMessage")

    class Config:
        populate_by_name = True


# GENERATION MODE - Request/Response Models
class ConversationGenerateRequest(BaseModel):
    """Request model for conversation generation endpoint (no editing context)."""
    message: str = Field(..., description="User's message", min_length=1)
    id: Optional[str] = Field(default=None, description="MongoDB conversation _id (if updating existing conversation)", alias="_id")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity", alias="sessionId")
    user_profile: UserProfile = Field(..., description="User profile with RBAC information", alias="userProfile")
    accessible_documents: List[DocumentAccess] = Field(
        default_factory=list,
        description="Documents user has access to",
        alias="accessibleDocuments"
    )
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "message": "I need to create a presentation about Q3 operational performance",
                "_id": "69050c25d3a3aea3ac48a6ad",
                "sessionId": "session_789",
                "userProfile": {
                    "userId": "user_456",
                    "name": "John Doe",
                    "role": "senior_analyst",
                    "department": "operations",
                    "accessScopes": ["operational_data", "internal_metrics"],
                    "permissions": {
                        "viewFinancialData": False,
                        "viewOperationalData": True,
                        "viewHRData": False,
                        "viewSalesData": False,
                        "viewConfidentialData": False,
                        "exportReports": True
                    }
                },
                "accessibleDocuments": [
                    {
                        "documentId": "doc_001",
                        "documentName": "Q3_Operations_Report.pdf",
                        "docType": "operations_report",
                        "department": "operations",
                        "accessLevel": "internal",
                        "summary": "Q3 operational metrics and KPIs",
                        "tags": ["operations", "Q3", "performance"],
                        "topics": ["efficiency", "productivity"]
                    }
                ],
                "context": {}
            }
        }


# EDITING MODE - Request/Response Models
class PreviousResponse(BaseModel):
    """Previous presentation response for editing mode."""
    presentation_id: Optional[str] = Field(default=None, alias="presentationId")
    previous_generated_outline: Optional[Dict[str, Any]] = Field(default=None, alias="previousGeneratedOutline")
    previous_generated_content: Optional[Dict[str, Any]] = Field(default=None, alias="previousGeneratedContent")
    slide_content: Optional[Dict[str, Any]] = Field(default=None, alias="slideContent")

    class Config:
        populate_by_name = True


class EditingContext(BaseModel):
    """Editing context for editing mode."""
    is_editing: bool = Field(..., alias="isEditing")
    previous_response: Optional[PreviousResponse] = Field(default=None, alias="previousResponse")
    edit_query: str = Field(..., description="The edit request from user", alias="editQuery")
    target_slide: Optional[int] = Field(default=None, alias="targetSlide")
    edit_type: Optional[EditType] = Field(default=None, alias="editType")

    class Config:
        populate_by_name = True


class ConversationEditRequest(BaseModel):
    """Request model for conversation editing endpoint (editing context required)."""
    message: str = Field(..., description="User's edit message", min_length=1)
    id: Optional[str] = Field(default=None, description="MongoDB conversation _id (if updating existing conversation)", alias="_id")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity", alias="sessionId")
    user_profile: UserProfile = Field(..., description="User profile with RBAC information", alias="userProfile")
    accessible_documents: List[DocumentAccess] = Field(
        default_factory=list,
        description="Documents user has access to (for RBAC validation)",
        alias="accessibleDocuments"
    )
    editing_context: EditingContext = Field(..., description="Context for editing mode (REQUIRED)", alias="editingContext")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "message": "Make slide 3 focus on efficiency metrics instead of productivity",
                "_id": "69050c25d3a3aea3ac48a6ad",
                "sessionId": "session_790",
                "userProfile": {
                    "userId": "user_456",
                    "name": "John Doe",
                    "role": "senior_analyst",
                    "department": "operations",
                    "accessScopes": ["operational_data", "internal_metrics"],
                    "permissions": {
                        "viewFinancialData": False,
                        "viewOperationalData": True,
                        "viewHRData": False,
                        "viewSalesData": False,
                        "viewConfidentialData": False,
                        "exportReports": True
                    }
                },
                "accessibleDocuments": [
                    {
                        "documentId": "doc_001",
                        "documentName": "Q3_Operations_Report.pdf",
                        "docType": "operations_report",
                        "department": "operations",
                        "accessLevel": "internal",
                        "summary": "Q3 operational metrics and KPIs",
                        "tags": ["operations", "Q3", "performance"],
                        "topics": ["efficiency", "productivity"]
                    }
                ],
                "editingContext": {
                    "isEditing": True,
                    "previousResponse": {
                        "presentationId": "pres_123",
                        "previousGeneratedOutline": {
  "presentation": {
    "title": "Q3 Operations Report",
    "total_slides": 10,
    "slides": [
      {
        "slide_number": 1,
        "title": "Title Slide",
        "content": [
          "Q3 Operations Report",
          "Quarter 3, [Year]",
          "[Company Name]"
        ]
      },
      {
        "slide_number": 2,
        "title": "Executive Summary",
        "content": [
          "Key highlights and achievements",
          "Critical metrics overview",
          "Major challenges addressed"
        ]
      },
      {
        "slide_number": 3,
        "title": "Operational Performance Metrics",
        "content": [
          "Production/output volumes",
          "Efficiency rates",
          "Quality metrics",
          "Year-over-year comparisons"
        ]
      },
      {
        "slide_number": 4,
        "title": "Financial Performance",
        "content": [
          "Revenue vs. budget",
          "Cost management",
          "Profit margins",
          "ROI on operational initiatives"
        ]
      },
      {
        "slide_number": 5,
        "title": "Team & Workforce",
        "content": [
          "Headcount changes",
          "Productivity metrics",
          "Training and development",
          "Employee satisfaction/retention"
        ]
      },
      {
        "slide_number": 6,
        "title": "Key Projects & Initiatives",
        "content": [
          "Major projects completed",
          "Ongoing initiatives",
          "Timeline and milestones achieved"
        ]
      },
      {
        "slide_number": 7,
        "title": "Challenges & Issues",
        "content": [
          "Obstacles encountered",
          "Supply chain or resource constraints",
          "Risk factors",
          "Mitigation strategies implemented"
        ]
      },
      {
        "slide_number": 8,
        "title": "Process Improvements",
        "content": [
          "Efficiency gains",
          "Technology implementations",
          "Best practices adopted",
          "Cost savings realized"
        ]
      },
      {
        "slide_number": 9,
        "title": "Q4 Outlook & Priorities",
        "content": [
          "Strategic goals for next quarter",
          "Planned initiatives",
          "Resource requirements",
          "Expected outcomes"
        ]
      },
      {
        "slide_number": 10,
        "title": "Conclusion & Next Steps",
        "content": [
          "Summary of key takeaways",
          "Action items",
          "Q&A"
        ]
      }
    ]
  }
},
                        "previousGeneratedContent": {},
                        "slideContent": {}
                    },
                    "editQuery": "Make slide 3 focus on productivity instead of efficiency metrics",
                    "targetSlide": 3,
                    "editType": "content"
                },
                "context": {}
            }
        }


# Shared Response Model
class ConversationResponse(BaseModel):
    """Response model for both generation and editing endpoints."""
    response: str = Field(..., description="Agent's response message")
    session_id: str = Field(..., description="Session ID", alias="sessionId")
    is_complete: bool = Field(..., description="Whether information gathering is complete", alias="isComplete")
    extracted_information: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted requirements",
        alias="extractedInformation"
    )
    rbac_validation: RBACValidation = Field(..., description="RBAC validation result", alias="rbacValidation")
    rbac_concerns: List[str] = Field(
        default_factory=list,
        description="RBAC-related concerns",
        alias="rbacConcerns"
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="Missing information items",
        alias="missingInformation"
    )
    confidence_score: float = Field(default=0.0, description="Confidence in completeness (0-1)", alias="confidenceScore")
    conversation_state: str = Field(..., description="Current conversation state", alias="conversationState")
    next_action: str = Field(..., description="Next action to take", alias="nextAction")
    handoff_to_agent: Optional[str] = Field(default=None, description="Agent to handoff to", alias="handoffToAgent")
    rbac_warnings: List[str] = Field(
        default_factory=list,
        description="RBAC warnings",
        alias="rbacWarnings"
    )
    suggested_documents: List[str] = Field(
        default_factory=list,
        description="Suggested documents",
        alias="suggestedDocuments"
    )
    cycle_type: str = Field(..., description="Current cycle type", alias="cycleType")
    timestamp: str = Field(..., description="Response timestamp")

    class Config:
        populate_by_name = True


# Other shared models
class ResetSessionRequest(BaseModel):
    """Request model for resetting a session."""
    session_id: str = Field(..., description="Session ID to reset", alias="sessionId")

    class Config:
        populate_by_name = True


class SessionInfoResponse(BaseModel):
    """Response model for session info."""
    session_id: str = Field(..., alias="sessionId")
    exists: bool
    message_count: int = Field(..., alias="messageCount")
    is_complete: bool = Field(..., alias="isComplete")
    extracted_info: Dict[str, Any] = Field(..., alias="extractedInfo")
    user_profile: Optional[Dict[str, Any]] = Field(default=None, alias="userProfile")
    rbac_warnings: List[str] = Field(default_factory=list, alias="rbacWarnings")
    cycle_type: Optional[str] = Field(default=None, alias="cycleType")

    class Config:
        populate_by_name = True


class GeneratePresentationRequest(BaseModel):
    """Request model for full workflow generation."""
    user_request: str = Field(..., description="User's presentation request", alias="userRequest")
    documents: Optional[List[str]] = Field(default=None, description="Document paths")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")

    class Config:
        populate_by_name = True


# ENDPOINTS

@router.post("/conversation-generate", response_model=ConversationResponse, tags=["agents"])
async def conversation_generate_endpoint(
    request: Request,
    conversation_request: ConversationGenerateRequest = Body(...)
):
    """
    Conversation endpoint for GENERATION MODE - gathering requirements for new presentation.

    This endpoint is specifically for creating NEW presentations. It will:
    1. Gather presentation requirements through natural conversation
    2. Enforce RBAC based on user profile
    3. Suggest accessible documents
    4. Ask clarifying questions until all requirements are gathered
    5. Hand off to Document Selection Agent when complete

    **RBAC Features:**
    - User profile-based personalization
    - Access scope validation
    - Permission-based content filtering
    - Graceful handling of out-of-scope requests

    **Workflow:**
    1. Send initial message with user profile and accessible documents
    2. Agent asks clarifying questions within user's scope
    3. Continue conversation until `isComplete` is True
    4. Use extracted information for presentation generation

    **Session Management:**
    - Provide `sessionId` to maintain conversation continuity
    - If no `sessionId` provided, a new session will be created
    - Sessions are stored in memory (use Redis in production)
    """
    try:
        # Get session ID or create new one
        session_id = conversation_request.session_id
        if not session_id:
            # Create new session ID if not provided
            import uuid
            session_id = f"gen_{uuid.uuid4().hex[:12]}"
            logger.info("creating_new_session", session_id=session_id)

        # Get or create conversation agent for this session
        if session_id not in conversation_sessions:
            logger.info(
                "initializing_conversation_agent_generation_mode",
                session_id=session_id,
                user_name=conversation_request.user_profile.name,
                department=conversation_request.user_profile.department
            )
            agent = ConversationAgent()
            conversation_sessions[session_id] = agent
            
            # Initialize agent with user profile for GENERATION mode
            agent.set_user_profile(conversation_request.user_profile.model_dump(by_alias=True))
            agent.set_accessible_documents([doc.model_dump(by_alias=True) for doc in conversation_request.accessible_documents])
            agent.set_cycle_type("generation")  # Explicitly set to generation mode
        else:
            agent = conversation_sessions[session_id]
            logger.info("reusing_existing_generation_session", session_id=session_id)
            
            # Update accessible documents if changed
            agent.set_accessible_documents([doc.model_dump(by_alias=True) for doc in conversation_request.accessible_documents])

        # Create agent request with GENERATION context (NO editing context)
        agent_request = AgentRequest(
            user_input=conversation_request.message,
            context={
                "cycleType": "generate",
                "userProfile": conversation_request.user_profile.model_dump(by_alias=True),
                "accessibleDocuments": [doc.model_dump(by_alias=True) for doc in conversation_request.accessible_documents],
                **conversation_request.context
            },
            session_id=session_id
        )

        # Execute agent
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error(
                "conversation_agent_failed_generation",
                session_id=session_id,
                user_id=conversation_request.user_profile.user_id,
                errors=response.errors
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Conversation agent failed",
                    "errors": response.errors,
                    "session_id": session_id
                }
            )

        output = response.output

        logger.info(
            "generation_response_generated",
            session_id=session_id,
            user_id=conversation_request.user_profile.user_id,
            is_complete=output.get("is_complete", False),
            confidence=output.get("confidence_score", 0),
            rbac_warnings_count=len(output.get("rbac_warnings", []))
        )

        # Save conversation to MongoDB
        try:
            conversations_collection = get_collection("conversations")

            # Create message documents
            user_message = ConversationMessage(
                role="user",
                content=conversation_request.message,
                timestamp=datetime.utcnow()
            )

            assistant_message = ConversationMessage(
                role="assistant",
                content=output.get("response", ""),
                timestamp=datetime.utcnow()
            )

            # Convert snake_case to camelCase for MongoDB
            from bson import ObjectId

            def snake_to_camel(data):
                """Recursively convert snake_case keys to camelCase."""
                if isinstance(data, dict):
                    return {
                        ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(k.split('_'))): snake_to_camel(v)
                        for k, v in data.items()
                    }
                elif isinstance(data, list):
                    return [snake_to_camel(item) for item in data]
                else:
                    return data

            extracted_info_dict = output.get("extracted_information", {})
            logger.info("pre_conversion", extracted_info=extracted_info_dict, confidence=extracted_info_dict.get("confidence_score"))

            # Convert to camelCase for MongoDB
            extracted_info = snake_to_camel(extracted_info_dict)
            logger.info("post_conversion", extracted_info=extracted_info, confidence=extracted_info.get("confidenceScore"))

            # The conversation should already exist (blank conversation created by frontend)
            # Frontend sends _id field if updating existing conversation
            existing_conv = None

            # Priority 1: Check if _id field was provided
            if conversation_request.id:
                try:
                    conversation_object_id = ObjectId(conversation_request.id)
                    existing_conv = await conversations_collection.find_one({"_id": conversation_object_id})
                    logger.info("looking_up_by_id", _id=conversation_request.id, found=existing_conv is not None)
                except Exception as e:
                    logger.error("invalid_id_format", _id=conversation_request.id, error=str(e))

            # Priority 2: Try session_id if it looks like an ObjectId
            if not existing_conv and session_id:
                try:
                    conversation_object_id = ObjectId(session_id)
                    existing_conv = await conversations_collection.find_one({"_id": conversation_object_id})
                    logger.info("looking_up_by_session_as_id", session_id=session_id, found=existing_conv is not None)
                except Exception:
                    pass  # session_id is not a valid ObjectId

            # Priority 3: Try finding by sessionId field
            if not existing_conv and session_id:
                existing_conv = await conversations_collection.find_one({"sessionId": session_id})
                logger.info("looking_up_by_session_id_field", session_id=session_id, found=existing_conv is not None)

            if existing_conv:
                # Update the existing conversation with messages and extracted info
                update_query = {"_id": existing_conv["_id"]}

                # extractedInfo should be an object (not an array)
                await conversations_collection.update_one(
                    update_query,
                    {
                        "$push": {
                            "messages": {
                                "$each": [
                                    user_message.model_dump(by_alias=True),
                                    assistant_message.model_dump(by_alias=True)
                                ]
                            }
                        },
                        "$set": {
                            "extractedInfo": extracted_info,
                            "updatedAt": datetime.utcnow(),
                            "totalCallsMade": output.get("tool_calls_made", 0),
                            "nextAction": output.get("next_action", "continue_conversation"),
                            "handOffToAgent": output.get("handoff_to_agent")
                        }
                    }
                )

                # Use the existing sessionId from the document, not the input
                actual_session_id = existing_conv.get("sessionId", str(existing_conv["_id"]))
                logger.info("conversation_updated_in_mongodb", session_id=actual_session_id, doc_id=str(existing_conv["_id"]))
            else:
                # Create new conversation
                # Generate a custom sessionId
                import uuid
                custom_session_id = f"session_{uuid.uuid4()}"

                # Build RBAC validation object
                rbac_validation_dict = output.get("rbac_validation", {})
                rbac_validation_obj = {
                    "validationResult": rbac_validation_dict.get("validation_result", "allowed"),
                    "allowedItems": rbac_validation_dict.get("allowed_items", []),
                    "deniedItems": rbac_validation_dict.get("denied_items", []),
                    "explanation": rbac_validation_dict.get("explanation", ""),
                    "suggestedAlternatives": rbac_validation_dict.get("suggested_alternatives", []),
                    "professionalMessage": rbac_validation_dict.get("professional_message")
                }

                conversation_doc = ConversationDocument(
                    sessionId=custom_session_id,
                    userId=conversation_request.user_profile.user_id,
                    cycleType="active",
                    messages=[user_message, assistant_message],
                    extractedInfo=extracted_info,
                    rbacValidation=rbac_validation_obj,
                    totalCallsMade=output.get("tool_calls_made", 0),
                    nextAction=output.get("next_action", "continue_conversation"),
                    handOffToAgent=output.get("handoff_to_agent"),
                    createdAt=datetime.utcnow(),
                    updatedAt=datetime.utcnow()
                )

                result = await conversations_collection.insert_one(
                    conversation_doc.model_dump(by_alias=True, exclude_none=True)
                )
                session_id = custom_session_id  # Update session_id to return the new one
                logger.info("conversation_created_in_mongodb", session_id=custom_session_id, doc_id=str(result.inserted_id))

        except Exception as db_error:
            logger.error(
                "mongodb_save_failed",
                session_id=session_id,
                error=str(db_error)
            )
            # Don't fail the request if DB save fails

        # Build RBAC validation response
        rbac_validation = output.get("rbac_validation", {})
        rbac_validation_response = RBACValidation(
            validation_result=rbac_validation.get("validation_result", "allowed"),
            allowed_items=rbac_validation.get("allowed_items", []),
            denied_items=rbac_validation.get("denied_items", []),
            explanation=rbac_validation.get("explanation", ""),
            suggested_alternatives=rbac_validation.get("suggested_alternatives", []),
            professional_message=rbac_validation.get("professional_message")
        )

        return ConversationResponse(
            response=output.get("response", ""),
            session_id=session_id,
            is_complete=output.get("is_complete", False),
            extracted_information=output.get("extracted_information", {}),
            rbac_validation=rbac_validation_response,
            rbac_concerns=output.get("rbac_concerns", []),
            missing_information=output.get("missing_information", []),
            confidence_score=output.get("confidence_score", 0.0),
            conversation_state=output.get("conversation_state", "gathering"),
            next_action=output.get("next_action", "continue_conversation"),
            handoff_to_agent=output.get("handoff_to_agent"),
            rbac_warnings=output.get("rbac_warnings", []),
            suggested_documents=output.get("suggested_documents", []),
            cycle_type="generate",
            timestamp=output.get("timestamp", "")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "generation_endpoint_error",
            error=str(e),
            error_type=type(e).__name__,
            user_id=conversation_request.user_profile.user_id
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation-edit", response_model=ConversationResponse, tags=["agents"])
async def conversation_edit_endpoint(
    request: Request,
    conversation_request: ConversationEditRequest = Body(...)
):
    """
    Conversation endpoint for EDITING MODE - processing modifications to existing presentations.

    This endpoint is specifically for EDITING existing presentations. It will:
    1. Classify the type of edit (content/visual/structure)
    2. Validate RBAC for the edit request
    3. Determine which agent should handle the edit
    4. Route to appropriate agent (Content/Image/Outline/Format Agent)

    **Edit Types:**
    - **Content**: Text changes, data updates, metric modifications
    - **Visual**: Chart changes, color schemes, image updates
    - **Structure**: Slide reordering, adding/removing slides
    - **General**: Ambiguous requests requiring clarification

    **RBAC Features:**
    - Validates edit requests against user permissions
    - Ensures edited content stays within access scope
    - Graceful handling of out-of-scope edit requests

    **Workflow:**
    1. Send edit message with editing context (previous presentation required)
    2. Agent classifies the edit type and scope
    3. Agent validates RBAC compliance
    4. Returns with handoff information to target agent

    **Session Management:**
    - Can reuse generation session or create new session
    - `sessionId` maintains conversation continuity
    """
    try:
        # Get session ID or create new one
        session_id = conversation_request.session_id
        if not session_id:
            # Create new session ID if not provided
            import uuid
            session_id = f"gen_{uuid.uuid4().hex[:12]}"
            logger.info("creating_new_session", session_id=session_id)

        # Get or create conversation agent for this session
        if session_id not in conversation_sessions:
            logger.info(
                "initializing_conversation_agent_editing_mode",
                session_id=session_id,
                user_name=conversation_request.user_profile.name,
                edit_type=conversation_request.editing_context.edit_type
            )
            agent = ConversationAgent()
            conversation_sessions[session_id] = agent
            
            # Initialize agent with user profile for EDITING mode
            agent.set_user_profile(conversation_request.user_profile.model_dump(by_alias=True))
            agent.set_accessible_documents([doc.model_dump(by_alias=True) for doc in conversation_request.accessible_documents])
            agent.set_cycle_type("edit")  # Explicitly set to editing mode
            agent.set_editing_context(conversation_request.editing_context.model_dump(by_alias=True))
        else:
            agent = conversation_sessions[session_id]
            logger.info("reusing_existing_editing_session", session_id=session_id)

            # Update accessible documents if changed
            agent.set_accessible_documents([doc.model_dump(by_alias=True) for doc in conversation_request.accessible_documents])

            # Update cycle type and editing context
            agent.set_cycle_type("edit")
            agent.set_editing_context(conversation_request.editing_context.model_dump(by_alias=True))

        # Create agent request with EDITING context
        agent_request = AgentRequest(
            user_input=conversation_request.message,
            context={
                "cycleType": "edit",
                "userProfile": conversation_request.user_profile.model_dump(by_alias=True),
                "accessibleDocuments": [doc.model_dump(by_alias=True) for doc in conversation_request.accessible_documents],
                "editingContext": conversation_request.editing_context.model_dump(by_alias=True),
                **conversation_request.context
            },
            session_id=session_id
        )

        # Execute agent
        response = await agent.execute(agent_request)

        if not response.success:
            logger.error(
                "conversation_agent_failed_editing",
                session_id=session_id,
                user_id=conversation_request.user_profile.user_id,
                errors=response.errors
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Conversation agent failed",
                    "errors": response.errors,
                    "session_id": session_id
                }
            )

        output = response.output

        logger.info(
            "editing_response_generated",
            session_id=session_id,
            user_id=conversation_request.user_profile.user_id,
            is_complete=output.get("is_complete", False),
            handoff_agent=output.get("handoff_to_agent"),
            edit_type=conversation_request.editing_context.edit_type
        )

        # Save conversation to MongoDB
        try:
            conversations_collection = get_collection("conversations")

            # Create message documents
            user_message = ConversationMessage(
                role="user",
                content=conversation_request.message,
                timestamp=datetime.utcnow()
            )

            assistant_message = ConversationMessage(
                role="assistant",
                content=output.get("response", ""),
                timestamp=datetime.utcnow()
            )

            # Convert snake_case to camelCase for MongoDB
            from bson import ObjectId

            def snake_to_camel(data):
                """Recursively convert snake_case keys to camelCase."""
                if isinstance(data, dict):
                    return {
                        ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(k.split('_'))): snake_to_camel(v)
                        for k, v in data.items()
                    }
                elif isinstance(data, list):
                    return [snake_to_camel(item) for item in data]
                else:
                    return data

            extracted_info_dict = output.get("extracted_information", {})
            logger.info("pre_conversion", extracted_info=extracted_info_dict, confidence=extracted_info_dict.get("confidence_score"))

            # Convert to camelCase for MongoDB
            extracted_info = snake_to_camel(extracted_info_dict)
            logger.info("post_conversion", extracted_info=extracted_info, confidence=extracted_info.get("confidenceScore"))

            # The conversation should already exist (blank conversation created by frontend)
            # Frontend sends _id field if updating existing conversation
            existing_conv = None

            # Priority 1: Check if _id field was provided
            if conversation_request.id:
                try:
                    conversation_object_id = ObjectId(conversation_request.id)
                    existing_conv = await conversations_collection.find_one({"_id": conversation_object_id})
                    logger.info("editing_looking_up_by_id", _id=conversation_request.id, found=existing_conv is not None)
                except Exception as e:
                    logger.error("editing_invalid_id_format", _id=conversation_request.id, error=str(e))

            # Priority 2: Try session_id if it looks like an ObjectId
            if not existing_conv and session_id:
                try:
                    conversation_object_id = ObjectId(session_id)
                    existing_conv = await conversations_collection.find_one({"_id": conversation_object_id})
                    logger.info("editing_looking_up_by_session_as_id", session_id=session_id, found=existing_conv is not None)
                except Exception:
                    pass  # session_id is not a valid ObjectId

            # Priority 3: Try finding by sessionId field
            if not existing_conv and session_id:
                existing_conv = await conversations_collection.find_one({"sessionId": session_id})
                logger.info("editing_looking_up_by_session_id_field", session_id=session_id, found=existing_conv is not None)

            if existing_conv:
                # Update the existing conversation with messages and extracted info
                update_query = {"_id": existing_conv["_id"]}

                # extractedInfo should be an object (not an array)
                await conversations_collection.update_one(
                    update_query,
                    {
                        "$push": {
                            "messages": {
                                "$each": [
                                    user_message.model_dump(by_alias=True),
                                    assistant_message.model_dump(by_alias=True)
                                ]
                            }
                        },
                        "$set": {
                            "extractedInfo": extracted_info,
                            "updatedAt": datetime.utcnow(),
                            "totalCallsMade": output.get("tool_calls_made", 0),
                            "nextAction": output.get("next_action", "continue_conversation"),
                            "handOffToAgent": output.get("handoff_to_agent")
                        }
                    }
                )

                # Use the existing sessionId from the document, not the input
                actual_session_id = existing_conv.get("sessionId", str(existing_conv["_id"]))
                logger.info("editing_conversation_updated_in_mongodb", session_id=actual_session_id, doc_id=str(existing_conv["_id"]))
            else:
                # Create new conversation for editing
                # Generate a custom sessionId
                import uuid
                custom_session_id = f"session_{uuid.uuid4()}"

                # Build RBAC validation object
                rbac_validation_dict = output.get("rbac_validation", {})
                rbac_validation_obj = {
                    "validationResult": rbac_validation_dict.get("validation_result", "allowed"),
                    "allowedItems": rbac_validation_dict.get("allowed_items", []),
                    "deniedItems": rbac_validation_dict.get("denied_items", []),
                    "explanation": rbac_validation_dict.get("explanation", ""),
                    "suggestedAlternatives": rbac_validation_dict.get("suggested_alternatives", []),
                    "professionalMessage": rbac_validation_dict.get("professional_message")
                }

                conversation_doc = ConversationDocument(
                    sessionId=custom_session_id,
                    userId=conversation_request.user_profile.user_id,
                    cycleType="edit",
                    messages=[user_message, assistant_message],
                    extractedInfo=extracted_info,
                    rbacValidation=rbac_validation_obj,
                    totalCallsMade=output.get("tool_calls_made", 0),
                    nextAction=output.get("next_action", "continue_conversation"),
                    handOffToAgent=output.get("handoff_to_agent"),
                    createdAt=datetime.utcnow(),
                    updatedAt=datetime.utcnow()
                )

                result = await conversations_collection.insert_one(
                    conversation_doc.model_dump(by_alias=True, exclude_none=True)
                )
                session_id = custom_session_id  # Update session_id to return the new one
                logger.info("editing_conversation_created_in_mongodb", session_id=custom_session_id, doc_id=str(result.inserted_id))

        except Exception as db_error:
            logger.error(
                "mongodb_save_failed_editing",
                session_id=session_id,
                error=str(db_error)
            )
            # Don't fail the request if DB save fails

        # Build RBAC validation response
        rbac_validation = output.get("rbac_validation", {})
        rbac_validation_response = RBACValidation(
            validation_result=rbac_validation.get("validation_result", "allowed"),
            allowed_items=rbac_validation.get("allowed_items", []),
            denied_items=rbac_validation.get("denied_items", []),
            explanation=rbac_validation.get("explanation", ""),
            suggested_alternatives=rbac_validation.get("suggested_alternatives", []),
            professional_message=rbac_validation.get("professional_message")
        )

        return ConversationResponse(
            response=output.get("response", ""),
            session_id=session_id,
            is_complete=output.get("is_complete", False),
            extracted_information=output.get("extracted_information", {}),
            rbac_validation=rbac_validation_response,
            rbac_concerns=output.get("rbac_concerns", []),
            missing_information=output.get("missing_information", []),
            confidence_score=output.get("confidence_score", 0.0),
            conversation_state=output.get("conversation_state", "editing"),
            next_action=output.get("next_action", "request_clarification"),
            handoff_to_agent=output.get("handoff_to_agent"),
            rbac_warnings=output.get("rbac_warnings", []),
            suggested_documents=[],  # Not applicable in editing mode
            cycle_type="edit",
            timestamp=output.get("timestamp", "")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "editing_endpoint_error",
            error=str(e),
            error_type=type(e).__name__,
            user_id=conversation_request.user_profile.user_id
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/reset", tags=["agents"])
async def reset_conversation(reset_request: ResetSessionRequest):
    """
    Reset a conversation session (works for both generation and editing sessions).

    Clears all conversation history, extracted information, and RBAC data for the given session.
    """
    try:
        session_id = reset_request.session_id

        if session_id in conversation_sessions:
            agent = conversation_sessions[session_id]
            agent.reset_conversation()
            logger.info("conversation_reset", session_id=session_id)

            return {
                "message": "Conversation reset successfully",
                "sessionId": session_id
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("reset_conversation_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/session/{session_id}", response_model=SessionInfoResponse, tags=["agents"])
async def get_session_info(session_id: str):
    """
    Get information about a conversation session (generation or editing).

    Returns session status, message count, extracted information, and RBAC data.
    """
    try:
        if session_id not in conversation_sessions:
            return SessionInfoResponse(
                session_id=session_id,
                exists=False,
                message_count=0,
                is_complete=False,
                extracted_info={},
                user_profile=None,
                rbac_warnings=[],
                cycle_type=None
            )

        agent = conversation_sessions[session_id]

        return SessionInfoResponse(
            session_id=session_id,
            exists=True,
            message_count=len(agent.conversation_history),
            is_complete=agent.extracted_info.get("is_complete", False),
            extracted_info=agent.extracted_info,
            user_profile=agent.user_profile,
            rbac_warnings=agent.rbac_warnings,
            cycle_type=agent.cycle_type
        )

    except Exception as e:
        logger.error("get_session_info_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/session/{session_id}", tags=["agents"])
async def delete_session(session_id: str):
    """
    Delete a conversation session (generation or editing).

    Removes the session from memory.
    """
    try:
        if session_id in conversation_sessions:
            del conversation_sessions[session_id]
            logger.info("session_deleted", session_id=session_id)

            return {
                "message": "Session deleted successfully",
                "sessionId": session_id
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_session_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/sessions", tags=["agents"])
async def list_sessions():
    """
    List all active conversation sessions (both generation and editing).

    Returns a list of session IDs with their status, including RBAC information and mode.
    """
    try:
        sessions = []
        for session_id, agent in conversation_sessions.items():
            sessions.append({
                "sessionId": session_id,
                "messageCount": len(agent.conversation_history),
                "isComplete": agent.extracted_info.get("is_complete", False),
                "confidenceScore": agent.extracted_info.get("confidence_score", 0.0),
                "state": agent.conversation_state,
                "cycleType": agent.cycle_type,
                "userRole": agent.user_profile.get("role") if agent.user_profile else None,
                "department": agent.user_profile.get("department") if agent.user_profile else None,
                "rbacWarningsCount": len(agent.rbac_warnings)
            })

        return {
            "totalSessions": len(sessions),
            "sessions": sessions
        }

    except Exception as e:
        logger.error("list_sessions_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-presentation", tags=["agents"])
async def generate_presentation(
    request: Request,
    gen_request: GeneratePresentationRequest = Body(...)
):
    """
    Generate a complete presentation using the full agent workflow.

    This endpoint runs all agents in sequence:
    1. Query Agent - Extract intent and context
    2. RAG Engine - Retrieve relevant information
    3. Outline Agent - Generate presentation structure
    4. Content Agent - Expand outline into full content
    5. Image Agent - Specify visualizations
    6. QA Agent - Validate content accuracy
    7. Format Agent - Generate HTML presentation
    8. Validation Engine - Final completeness check

    **Note:** This can take 15-30 seconds depending on complexity.
    """
    try:
        # Get orchestrator from app state
        if not hasattr(request.app.state, "orchestrator"):
            # Initialize orchestrator on first use
            logger.info("initializing_agent_orchestrator")
            rag_client = getattr(request.app.state, "rag_client", None)
            orchestrator = AgentOrchestrator(rag_client=rag_client)
            await orchestrator.initialize()
            request.app.state.orchestrator = orchestrator
        else:
            orchestrator = request.app.state.orchestrator

        logger.info(
            "starting_presentation_generation",
            request_length=len(gen_request.user_request),
            has_documents=bool(gen_request.documents),
            preferences=gen_request.preferences
        )

        # Run full workflow
        result = await orchestrator.run_full_workflow(
            user_request=gen_request.user_request,
            documents=gen_request.documents,
            preferences=gen_request.preferences
        )

        if result["success"]:
            logger.info("presentation_generated_successfully")

            return {
                "success": True,
                "message": "Presentation generated successfully",
                "presentation": result["presentation"],
                "metadata": result["metadata"]
            }
        else:
            logger.error("presentation_generation_failed", error=result.get("error"))
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Presentation generation failed",
                    "message": result.get("error"),
                    "partial_outputs": result.get("partial_outputs", {})
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("generate_presentation_error", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/info", tags=["agents"])
async def agents_info():
    """
    Get information about available agents and their configurations.
    
    Includes information about RBAC support and dual-mode operation with separate endpoints.
    """
    from src.agents import list_agent_configs

    try:
        configs = list_agent_configs()

        return {
            "available_agents": [
                "conversation",
                "document_selection",
                "query",
                "rag_engine",
                "outline",
                "content",
                "image_coordination",
                "qa",
                "format",
                "validation"
            ],
            "agent_configs": configs,
            "workflows": {
                "conversation_generation": {
                    "description": "Interactive conversation to gather requirements for NEW presentation",
                    "endpoint": "/api/v1/agents/conversation-generate",
                    "mode": "generation",
                    "supports_rbac": True,
                    "requires_editing_context": False
                },
                "conversation_editing": {
                    "description": "Interactive conversation to process EDIT requests for existing presentations",
                    "endpoint": "/api/v1/agents/conversation-edit",
                    "mode": "editing",
                    "supports_rbac": True,
                    "requires_editing_context": True
                },
                "full_generation": {
                    "description": "Complete presentation generation workflow (bypasses conversation)",
                    "endpoint": "/api/v1/agents/generate-presentation",
                    "supports_rbac": False
                }
            },
            "rbac_features": {
                "user_profiles": True,
                "document_access_control": True,
                "permission_based_filtering": True,
                "access_scope_validation": True,
                "graceful_denial_handling": True
            },
            "endpoint_separation": {
                "reason": "Clear separation between generation and editing for better type safety and developer experience",
                "generation_endpoint": "/conversation-generate (no editingContext)",
                "editing_endpoint": "/conversation-edit (editingContext required)"
            }
        }

    except Exception as e:
        logger.error("agents_info_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))