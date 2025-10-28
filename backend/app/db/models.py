"""Pydantic models for MongoDB documents."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, EmailStr


# Base model with common fields
class MongoBaseModel(BaseModel):
    """Base model for MongoDB documents."""

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {}
        }


# User Profile Models
class UserPermissions(BaseModel):
    """User permissions for RBAC."""
    viewFinancialData: bool = False
    viewOperationalData: bool = False
    viewHRData: bool = False
    viewSalesData: bool = False
    viewConfidentialData: bool = False


class UserProfile(BaseModel):
    """User profile information."""
    name: str
    role: str
    department: str
    accessScopes: List[str] = Field(default_factory=list)
    permissions: UserPermissions = Field(default_factory=UserPermissions)


class UserDocument(MongoBaseModel):
    """User document stored in MongoDB."""
    userId: str
    email: EmailStr
    passwordHash: str
    profile: UserProfile
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


# Conversation Models
class ConversationMessage(BaseModel):
    """Single conversation message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PresentationRequirements(BaseModel):
    """Presentation requirements extracted from conversation."""
    topic: Optional[str] = None
    targetAudience: Optional[str] = None
    numSlides: Optional[int] = 10
    keyThemes: List[str] = Field(default_factory=list)
    tone: Optional[str] = None
    objectives: Optional[str] = None


class DataRequirements(BaseModel):
    """Data requirements for presentation."""
    documentsRequested: List[str] = Field(default_factory=list)
    contentToExtract: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    timePeriods: List[str] = Field(default_factory=list)
    comparisons: List[str] = Field(default_factory=list)
    dataCategories: List[str] = Field(default_factory=list)


class VisualPreferences(BaseModel):
    """Visual preferences for presentation."""
    chartTypes: List[str] = Field(default_factory=list)
    style: Optional[str] = None
    includeImages: Optional[bool] = None
    colorScheme: Optional[str] = None


class EditingRequirements(BaseModel):
    """Editing requirements for presentation modifications."""
    editType: Optional[str] = None  # content | visual | structure | general
    targetSlide: Optional[int] = None
    specificChanges: List[str] = Field(default_factory=list)
    editScope: Optional[str] = None  # single_slide | multiple_slides | entire_presentation


class ExtractedInformation(BaseModel):
    """Information extracted from conversation."""
    presentationRequirements: PresentationRequirements = Field(default_factory=PresentationRequirements)
    dataRequirements: DataRequirements = Field(default_factory=DataRequirements)
    visualPreferences: VisualPreferences = Field(default_factory=VisualPreferences)
    editingRequirements: Optional[EditingRequirements] = None
    rbacConcerns: List[str] = Field(default_factory=list)


class RBACValidation(BaseModel):
    """RBAC validation result."""
    validationResult: str = "allowed"  # allowed | partially_allowed | denied
    allowedItems: List[str] = Field(default_factory=list)
    deniedItems: List[str] = Field(default_factory=list)
    explanation: str = ""
    suggestedAlternatives: List[str] = Field(default_factory=list)
    professionalMessage: Optional[str] = None


class ConversationDocument(MongoBaseModel):
    """Conversation document stored in MongoDB."""
    sessionId: str
    userId: str
    cycleType: str = "generation"  # generation | editing
    messages: List[ConversationMessage] = Field(default_factory=list)
    extractedInfo: ExtractedInformation = Field(default_factory=ExtractedInformation)
    rbacValidation: RBACValidation = Field(default_factory=RBACValidation)
    missingInformation: List[str] = Field(default_factory=list)
    isComplete: bool = False
    confidenceScore: float = 0.0
    conversationState: str = "gathering"  # gathering | clarifying | validating | complete | editing
    nextAction: str = "continue_conversation"
    handoffToAgent: Optional[str] = None
    rbacWarnings: List[str] = Field(default_factory=list)
    suggestedDocuments: List[str] = Field(default_factory=list)
    toolCallsMade: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


# Document Models
class AccessibleDocument(MongoBaseModel):
    """Document metadata for RBAC filtering."""
    documentId: str
    documentName: str
    docType: str
    department: str
    accessLevel: str
    summary: str
    tags: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
