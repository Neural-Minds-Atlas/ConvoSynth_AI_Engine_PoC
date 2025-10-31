"""
Content Agent Data Models
Pydantic models for Content Agent input/output schemas
"""

from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# INPUT MODELS - From Conversation Agent
# ============================================================================

class DataRequirements(BaseModel):
    """Data requirements from conversation agent"""
    comparisons: List[str] = Field(default_factory=list, description="List of comparisons to make")
    contentToExtract: List[str] = Field(default_factory=list, description="Content items to extract")
    dataCategories: List[str] = Field(default_factory=list, description="Categories of data")
    documentsRequested: List[str] = Field(default_factory=list, description="Requested documents")
    metrics: List[str] = Field(default_factory=list, description="Metrics to analyze")
    timePeriods: List[str] = Field(default_factory=list, description="Time periods for analysis")


class PresentationRequirements(BaseModel):
    """Presentation requirements from conversation agent"""
    keyThemes: List[str] = Field(description="Key themes to cover")
    numSlides: int = Field(description="Number of slides")
    objectives: str = Field(description="Presentation objectives")
    targetAudience: str = Field(description="Target audience")
    tone: str = Field(description="Presentation tone")
    topic: str = Field(description="Main topic")


class VisualPreferences(BaseModel):
    """Visual preferences from conversation agent"""
    chartTypes: List[str] = Field(default_factory=list, description="Preferred chart types")
    colorScheme: str = Field(default="Professional", description="Color scheme")
    includeImages: bool = Field(default=True, description="Include images")
    style: str = Field(description="Visual style")


class ExtractedInformation(BaseModel):
    """Extracted information from conversation agent"""
    dataRequirements: DataRequirements
    presentationRequirements: PresentationRequirements
    visualPreferences: VisualPreferences


# ============================================================================
# INPUT MODELS - From Outline Agent
# ============================================================================

class DataMapping(BaseModel):
    """Data mapping for bullet points"""
    queryId: Optional[str] = Field(None, description="Query identifier")
    metricName: Optional[str] = Field(None, description="Metric name")
    dataType: Optional[str] = Field(None, description="Data type")


class BulletPoint(BaseModel):
    """Bullet point structure from outline"""
    bulletText: str = Field(description="Main bullet point text")
    subBullets: List[str] = Field(default_factory=list, description="Sub-bullet points")
    requiresData: bool = Field(default=False, description="Whether this requires data")
    dataMapping: Optional[DataMapping] = Field(None, description="Data mapping information")


class VisualHint(BaseModel):
    """Visual hint from outline agent"""
    visualType: str = Field(description="Type of visual element")
    chartType: Optional[str] = Field(None, description="Chart type")
    dataSource: Optional[str] = Field(None, description="Data source")
    purpose: str = Field(description="Purpose of the visual")


class SlideOutline(BaseModel):
    """Single slide outline from outline agent"""
    slideNumber: int = Field(description="Slide number")
    slideType: str = Field(description="Type of slide")
    title: str = Field(description="Slide title")
    bulletPoints: List[BulletPoint] = Field(default_factory=list, description="Bullet points")
    visualHints: List[VisualHint] = Field(default_factory=list, description="Visual hints")
    speakerNotes: Optional[str] = Field(None, description="Speaker notes")
    keyMessage: str = Field(description="Key message of the slide")


class DataIntegration(BaseModel):
    """Data integration metadata"""
    totalDataPoints: int = Field(default=0, description="Total data points")
    queriesReferenced: List[str] = Field(default_factory=list, description="Referenced queries")
    coverageScore: float = Field(default=0.0, description="Coverage score 0-1")


class EditingMetadata(BaseModel):
    """Editing metadata"""
    modifiedSlides: List[int] = Field(default_factory=list, description="Modified slide numbers")
    addedSlides: List[int] = Field(default_factory=list, description="Added slide numbers")
    removedSlides: List[int] = Field(default_factory=list, description="Removed slide numbers")
    structuralChanges: Optional[str] = Field(None, description="Description of structural changes")


class OutlineMetadata(BaseModel):
    """Outline metadata"""
    templateCompliance: bool = Field(description="Template compliance")
    slideCountCompliance: bool = Field(description="Slide count compliance")
    narrativeCoherence: float = Field(description="Narrative coherence score")
    dataIntegration: DataIntegration
    editingMetadata: Optional[EditingMetadata] = Field(None)


class QualityChecks(BaseModel):
    """Quality checks"""
    allSlidesHaveTitles: bool = Field(default=True)
    bulletPointsWithinLimit: bool = Field(default=True)
    visualHintsProvided: bool = Field(default=True)
    dataBackedClaims: bool = Field(default=True)
    logicalFlow: bool = Field(default=True)


class PresentationOutline(BaseModel):
    """Complete presentation outline from outline agent"""
    title: str = Field(description="Presentation title")
    subtitle: Optional[str] = Field(None, description="Presentation subtitle")
    totalSlides: int = Field(description="Total number of slides")
    narrativeFlow: Optional[str] = Field(None, description="Narrative flow description")
    slides: List[SlideOutline] = Field(description="List of slide outlines")


class OutlineAgentOutput(BaseModel):
    """Complete output from outline agent"""
    success: bool = Field(default=True)
    sessionId: str
    userId: str
    outlineId: str
    cycleType: str
    presentationOutline: PresentationOutline
    outlineMetadata: OutlineMetadata
    qualityChecks: QualityChecks
    nextAction: Optional[str] = Field(None)
    handoffToAgent: Optional[str] = Field(None)
    performanceMetrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    error: Optional[str] = Field(None)


# ============================================================================
# CONTENT AGENT INPUT
# ============================================================================

class ContentAgentInput(BaseModel):
    """Complete input for Content Agent"""
    sessionId: str = Field(description="Session identifier")
    userId: str = Field(description="User identifier")
    extractedInformation: ExtractedInformation = Field(description="From conversation agent")
    outlineAgentOutput: OutlineAgentOutput = Field(description="From outline agent")
    ragEndpoint: str = Field(
        default="http://localhost:8000/api/v1/query",
        description="RAG query endpoint"
    )


# ============================================================================
# OUTPUT MODELS - Content Agent Output
# ============================================================================

class ContentDataMapping(BaseModel):
    """Data mapping in expanded content"""
    metricName: str = Field(description="Metric name")
    dataValue: str = Field(description="Actual data value")


class ExpandedBulletPoint(BaseModel):
    """Expanded bullet point with content"""
    bulletTextContent: str = Field(description="Full bullet point content")
    subBulletsContent: List[str] = Field(default_factory=list, description="Sub-bullet content")
    requiresData: bool = Field(default=False, description="Whether this has data")
    dataMapping: List[ContentDataMapping] = Field(
        default_factory=list,
        description="Data mappings with values"
    )


class VisualElement(BaseModel):
    """Visual element with complete information for image agent"""
    visualType: str = Field(description="Type of visual (chart, image, diagram)")
    chartType: Optional[str] = Field(None, description="Specific chart type")
    dataSource: Optional[str] = Field(None, description="Source of data")
    dataValue: Optional[str] = Field(None, description="Actual data for visualization")
    purpose: str = Field(description="Purpose of this visual")
    xAxisLabel: Optional[str] = Field(None, description="X-axis label for charts")
    yAxisLabel: Optional[str] = Field(None, description="Y-axis label for charts")
    title: Optional[str] = Field(None, description="Chart/visual title")
    dataPoints: Optional[List[Dict[str, Any]]] = Field(None, description="Data points for plotting")
    colorScheme: Optional[str] = Field(None, description="Color scheme to use")
    annotations: Optional[List[str]] = Field(None, description="Annotations to add")


class ExpandedSlideContent(BaseModel):
    """Expanded content for a single slide"""
    slideNumber: int = Field(description="Slide number")
    slideType: str = Field(description="Type of slide")
    title: str = Field(description="Slide title")
    bulletPoints: List[ExpandedBulletPoint] = Field(
        default_factory=list,
        description="Expanded bullet points"
    )
    visualElements: List[VisualElement] = Field(
        default_factory=list,
        description="Complete visual elements for image agent"
    )
    speakerNotes: Optional[str] = Field(None, description="Detailed speaker notes")
    keyMessage: str = Field(description="Key message of the slide")


class ExpandedPresentationContent(BaseModel):
    """Complete expanded presentation content"""
    title: str = Field(description="Presentation title")
    subtitle: Optional[str] = Field(None, description="Presentation subtitle")
    totalSlides: int = Field(description="Total number of slides")
    slides: List[ExpandedSlideContent] = Field(description="Expanded slide content")


class ContentMetadata(BaseModel):
    """Content generation metadata"""
    slideCountCompliance: bool = Field(description="Slide count compliance")
    narrativeCoherence: float = Field(description="Narrative coherence score")
    dataIntegration: DataIntegration
    editingMetadata: Optional[EditingMetadata] = Field(None)
    ragQueriesMade: int = Field(default=0, description="Number of RAG queries made")
    dataPointsExtracted: int = Field(default=0, description="Data points extracted")
    citationsAdded: int = Field(default=0, description="Citations added")


class ContentQualityChecks(BaseModel):
    """Quality checks for content"""
    allSlidesHaveTitles: bool = Field(default=True)
    bulletPointsWithinLimit: bool = Field(default=True)
    visualElementsProvided: bool = Field(default=True)
    dataBackedClaims: bool = Field(default=True)
    logicalFlow: bool = Field(default=True)
    financialAccuracy: Optional[float] = Field(None, description="Financial accuracy score")


class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    responseTime: float = Field(description="Response time in seconds")
    agentIterations: int = Field(description="Number of agent iterations")
    toolCallsMade: int = Field(description="Number of tool calls made")


class ContentAgentOutput(BaseModel):
    """Complete output from Content Agent"""
    success: bool = Field(default=True)
    sessionId: str
    userId: str
    contentId: str
    cycleType: str
    expandedPresentationContent: ExpandedPresentationContent
    contentMetadata: ContentMetadata
    qualityChecks: ContentQualityChecks
    nextAction: Optional[str] = Field(None, description="Next action to take")
    handoffToAgent: Optional[str] = Field(None, description="Agent to hand off to")
    performanceMetrics: PerformanceMetrics
    timestamp: str
    error: Optional[str] = Field(None)


# ============================================================================
# RAG QUERY MODELS
# ============================================================================

class RAGQueryRequest(BaseModel):
    """Request model for RAG query endpoint"""
    query: str = Field(description="Query string")
    mode: Literal["hybrid", "naive", "local", "global"] = Field(
        default="hybrid",
        description="RAG retrieval mode"
    )
    top_k: int = Field(default=5, description="Number of results to retrieve", ge=1, le=20)
    use_llm_enhancement: bool = Field(default=True, description="Use LLM enhancement")
    system_prompt: str = Field(
        default="You are a helpful AI assistant that answers questions based STRICTLY on the provided context.",
        description="System prompt for RAG"
    )


class RAGQueryResponse(BaseModel):
    """Response model from RAG query endpoint"""
    query: str
    response: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
