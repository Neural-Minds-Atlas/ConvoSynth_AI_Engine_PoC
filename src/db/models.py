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
    missingInformation: List[str] = Field(default_factory=list, alias="missing_information")
    isComplete: bool = Field(default=False, alias="is_complete")
    confidenceScore: float = Field(default=0.0, alias="confidence_score")
    conversationState: str = Field(default="gathering", alias="conversation_state")

    class Config:
        populate_by_name = True


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
    presentationId: Optional[str] = None
    title: Optional[str] = None
    cycleType: str = "active"  # active | generation | editing
    messages: List[ConversationMessage] = Field(default_factory=list)
    extractedInfo: ExtractedInformation = Field(default_factory=ExtractedInformation)
    rbacValidation: RBACValidation = Field(default_factory=RBACValidation)
    nextAction: str = "idle"
    handOffToAgent: Optional[str] = Field(default=None, alias="handoffToAgent")
    rbacWarnings: List[str] = Field(default_factory=list)
    suggestedDocuments: List[str] = Field(default_factory=list)
    totalCallsMade: int = Field(default=0, alias="toolCallsMade")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


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


# =============================================================================
# MULTI-AGENT WORKFLOW MODELS - Production-Ready MongoDB Schemas
# =============================================================================

# Agent Execution Metadata
class AgentExecutionMetadata(BaseModel):
    """Metadata for agent execution tracking."""
    agentName: str
    agentType: str
    executionTime: float  # seconds
    tokenUsage: Optional[int] = None
    modelUsed: str
    temperature: float
    retryCount: int = 0
    success: bool = True
    errorMessage: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Query Agent Models - Match actual agent output structure
class QueryAgentOutput(BaseModel):
    """Output from Query Agent - stores exactly what agent outputs."""
    success: bool = True
    sessionId: str
    response: str
    generatedQueries: List[Dict[str, Any]] = Field(default_factory=list)  # Raw query objects
    synthesizedContext: Dict[str, Any] = Field(default_factory=dict)
    performanceMetrics: Dict[str, Any] = Field(default_factory=dict)
    toolCallsMade: int = 0
    timestamp: str
    error: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)


# Document Selection Agent Models
class SelectedDocument(BaseModel):
    """Document selected by Document Selection Agent."""
    documentId: str
    documentName: str
    relevanceScore: float
    selectionReason: str
    documentType: str
    keyTopics: List[str] = Field(default_factory=list)


class DocumentSelectionOutput(BaseModel):
    """Output from Document Selection Agent."""
    selectedDocuments: List[SelectedDocument] = Field(default_factory=list)
    totalDocumentsEvaluated: int
    selectionCriteria: List[str] = Field(default_factory=list)
    rejectedDocuments: List[Dict[str, Any]] = Field(default_factory=list)


# RAG Engine Models
class RAGEngineOutput(BaseModel):
    """Output from RAG Engine Agent."""
    retrievedContext: str
    sourceDocuments: List[str] = Field(default_factory=list)
    chunkSummaries: List[Dict[str, Any]] = Field(default_factory=list)
    keyFindings: List[str] = Field(default_factory=list)
    confidenceScore: float
    totalChunksRetrieved: int
    ragMode: str


# Outline Agent Models - Match actual agent output structure
class OutlineAgentOutput(BaseModel):
    """Output from Outline Agent - stores exactly what agent outputs."""
    success: bool = True
    sessionId: str
    userId: str
    outlineId: str
    cycleType: str
    presentationOutline: Dict[str, Any]  # Raw outline object with title, subtitle, slides, etc.
    outlineMetadata: Dict[str, Any]  # Raw metadata object
    qualityChecks: Dict[str, Any]  # Raw quality checks object
    nextAction: str
    handoffToAgent: Optional[str] = None
    performanceMetrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    error: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)


# Content Agent Models - Match actual agent output structure
class ContentAgentOutput(BaseModel):
    """Output from Content Agent - stores exactly what agent outputs."""
    success: bool = True
    sessionId: str
    userId: str
    contentId: str
    cycleType: str
    expandedPresentationContent: Dict[str, Any]  # Raw content object with title, subtitle, slides
    contentMetadata: Dict[str, Any]  # Raw metadata object
    qualityChecks: Dict[str, Any]  # Raw quality checks object
    nextAction: str
    handoffToAgent: Optional[str] = None
    performanceMetrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    error: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)


# Image Coordination Agent Models
class VisualSpecification(BaseModel):
    """Visual specification for a slide."""
    slideNumber: int
    visualType: str  # chart, graph, image, diagram, table
    chartType: Optional[str] = None  # bar, line, pie, scatter
    dataSource: str
    title: str
    description: str
    specifications: Dict[str, Any] = Field(default_factory=dict)  # colors, axes, labels


class ImageCoordinationOutput(BaseModel):
    """Output from Image Coordination Agent."""
    visualSpecs: List[VisualSpecification] = Field(default_factory=list)
    totalVisuals: int
    visualTheme: str
    colorScheme: List[str] = Field(default_factory=list)


# Format Agent Models
class FormattedSlide(BaseModel):
    """Formatted slide in HTML."""
    slideNumber: int
    html: str
    cssClasses: List[str] = Field(default_factory=list)
    visualElements: List[str] = Field(default_factory=list)


class FormatAgentOutput(BaseModel):
    """Output from Format Agent."""
    slides: List[FormattedSlide] = Field(default_factory=list)
    fullHtml: str
    cssStyles: str
    totalSlides: int
    theme: str


# QA Agent Models
class QAValidation(BaseModel):
    """Quality assurance validation result."""
    category: str  # accuracy, completeness, consistency, clarity
    status: str  # pass, warning, fail
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class QAAgentOutput(BaseModel):
    """Output from QA Agent."""
    overallScore: float  # 0-1
    passedValidations: List[QAValidation] = Field(default_factory=list)
    failedValidations: List[QAValidation] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    criticalIssues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# Validation Engine Models
class ValidationResult(BaseModel):
    """Final validation result."""
    validationType: str  # completeness, format, accessibility, business_rules
    passed: bool
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ValidationEngineOutput(BaseModel):
    """Output from Validation Engine."""
    isValid: bool
    validationResults: List[ValidationResult] = Field(default_factory=list)
    overallScore: float  # 0-1
    readyForDelivery: bool
    issues: List[str] = Field(default_factory=list)


# =============================================================================
# WORKFLOW DOCUMENT - Complete End-to-End Workflow State
# =============================================================================

class WorkflowDocument(MongoBaseModel):
    """Complete workflow state stored in MongoDB - Production Ready."""

    # Workflow Identification
    workflowId: str  # UUID for entire workflow
    sessionId: str  # Links to conversation
    userId: str  # User who initiated
    status: str = "in_progress"  # in_progress, completed, failed, cancelled

    # Timestamps
    startedAt: datetime = Field(default_factory=datetime.utcnow)
    completedAt: Optional[datetime] = None
    totalExecutionTime: Optional[float] = None  # seconds

    # Input Context
    userInput: str
    conversationOutput: Optional[ExtractedInformation] = None
    documents: List[str] = Field(default_factory=list)
    userPreferences: Dict[str, Any] = Field(default_factory=dict)

    # Agent Outputs (Sequential Pipeline)
    queryAgentOutput: Optional[QueryAgentOutput] = None
    documentSelectionOutput: Optional[DocumentSelectionOutput] = None
    ragEngineOutput: Optional[RAGEngineOutput] = None
    outlineAgentOutput: Optional[OutlineAgentOutput] = None
    contentAgentOutput: Optional[ContentAgentOutput] = None
    imageCoordinationOutput: Optional[ImageCoordinationOutput] = None
    formatAgentOutput: Optional[FormatAgentOutput] = None
    qaAgentOutput: Optional[QAAgentOutput] = None
    validationEngineOutput: Optional[ValidationEngineOutput] = None

    # Agent Execution Tracking
    agentExecutions: List[AgentExecutionMetadata] = Field(default_factory=list)
    currentStage: str = "conversation"  # conversation, query, document_selection, etc.
    failedStage: Optional[str] = None

    # Final Output
    finalPresentation: Optional[Dict[str, Any]] = None
    presentationHtml: Optional[str] = None
    presentationMetadata: Dict[str, Any] = Field(default_factory=dict)

    # Performance Metrics
    latencyBreakdown: Dict[str, float] = Field(default_factory=dict)
    totalTokensUsed: int = 0
    totalCost: Optional[float] = None

    # Error Handling
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    retries: int = 0

    # Metadata
    version: str = "1.0.0"
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
