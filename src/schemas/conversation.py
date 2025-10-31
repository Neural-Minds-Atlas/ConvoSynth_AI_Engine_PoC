"""Conversation-related schemas."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.db.models import (
    UserProfile,
    AccessibleDocument,
    ExtractedInformation,
    RBACValidation,
    ConversationMessage,
)


class EditingContext(BaseModel):
    """Context for editing mode."""
    isEditing: bool
    previousResponse: Dict[str, Any] = Field(default_factory=dict)
    editQuery: Optional[str] = None
    targetSlide: Optional[int] = None
    editType: Optional[str] = None  # content | visual | structure | general


class ConversationRequest(BaseModel):
    """Schema for conversation request."""
    sessionId: Optional[str] = None  # If None, a new session will be created
    userMessage: str
    cycleType: str = "generation"  # generation | editing
    editingContext: Optional[EditingContext] = None

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "sess_789abc",
                "userMessage": "I need to create a presentation about Q3 operational performance",
                "cycleType": "generation",
                "editingContext": None
            }
        }


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    sessionId: str
    messageId: str
    response: str
    isComplete: bool
    extractedInformation: ExtractedInformation
    rbacValidation: RBACValidation
    rbacConcerns: List[str]
    missingInformation: List[str]
    confidenceScore: float
    conversationState: str
    nextAction: str
    handoffToAgent: Optional[str]
    rbacWarnings: List[str]
    suggestedDocuments: List[str]
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "sess_789abc",
                "messageId": "msg_001",
                "response": "Hi John! I'd be happy to help you create an operational performance presentation...",
                "isComplete": False,
                "extractedInformation": {
                    "presentationRequirements": {
                        "topic": "Q3 operational performance",
                        "targetAudience": None,
                        "numSlides": 10,
                        "keyThemes": ["operational performance"],
                        "tone": None,
                        "objectives": None
                    },
                    "dataRequirements": {},
                    "visualPreferences": {},
                    "editingRequirements": None,
                    "rbacConcerns": []
                },
                "rbacValidation": {
                    "validationResult": "allowed",
                    "allowedItems": [],
                    "deniedItems": [],
                    "explanation": "",
                    "suggestedAlternatives": [],
                    "professionalMessage": None
                },
                "rbacConcerns": [],
                "missingInformation": ["target_audience", "objectives"],
                "confidenceScore": 0.3,
                "conversationState": "gathering",
                "nextAction": "continue_conversation",
                "handoffToAgent": None,
                "rbacWarnings": [],
                "suggestedDocuments": [],
                "timestamp": "2025-10-22T10:30:00Z"
            }
        }


class ConversationHistoryResponse(BaseModel):
    """Schema for conversation history."""
    userId: str
    conversations: List[Dict[str, Any]]
    totalCount: int
    page: int
    pageSize: int


class SessionResetRequest(BaseModel):
    """Schema for session reset request."""
    sessionId: str


class SessionInfoResponse(BaseModel):
    """Schema for session info response."""
    sessionId: str
    userId: str
    cycleType: str
    messageCount: int
    isComplete: bool
    confidenceScore: float
    conversationState: str
    createdAt: datetime
    updatedAt: datetime
