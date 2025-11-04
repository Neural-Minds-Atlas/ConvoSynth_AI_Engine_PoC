"""API routes for Outline Agent - Generation and Editing endpoints."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, Field, validator

# Import test payloads for example request bodies
try:
    from .test_outline_payloads_complete import BDX_STOCK_ANALYSIS_COMPLETE
    # Use the complete payload including synthesizedContext, generatedQueries, and performanceMetrics
    if BDX_STOCK_ANALYSIS_COMPLETE:
        OUTLINE_GENERATE_EXAMPLE = BDX_STOCK_ANALYSIS_COMPLETE
    else:
        OUTLINE_GENERATE_EXAMPLE = None
except ImportError:
    OUTLINE_GENERATE_EXAMPLE = None

# Import edit payloads for edit endpoint examples
try:
    from .test_outline_edit_payload import (
        EDIT_EXAMPLE_MINIMAL,
        EDIT_EXAMPLE_GLOBAL_CONCISE,
        EDIT_EXAMPLE_SINGLE_SLIDE
    )
    OUTLINE_EDIT_EXAMPLES = {
        "minimal_edit": {
            "summary": "Minimal Edit Example (Quick Test)",
            "description": "Small 3-slide outline with simple edit request. Best for quick validation.",
            "value": EDIT_EXAMPLE_MINIMAL
        },
        "global_concise": {
            "summary": "Global Edit - Make Concise (Full BDX Data)",
            "description": "Complete 10-slide BDX stock analysis with request to make entire presentation more concise. Includes all 8 query results with full metadata.",
            "value": EDIT_EXAMPLE_GLOBAL_CONCISE
        },
        "single_slide_edit": {
            "summary": "Single Slide Edit - Add Emphasis (Full BDX Data)",
            "description": "Edit slide 5 to add emphasis on volatility reduction. Complete data with all query results.",
            "value": EDIT_EXAMPLE_SINGLE_SLIDE
        }
    }
except ImportError:
    OUTLINE_EDIT_EXAMPLES = None

# Assuming the agent is imported from the agents module
# Adjust import path based on your project structure
# from src.agents.outline.agent import OutlineAgent

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/outline",
    responses={404: {"description": "Not found"}}
)


# ===================== Request/Response Models =====================

class PresentationRequirements(BaseModel):
    """Presentation requirements model."""
    topic: str = Field(..., description="Main presentation topic")
    targetAudience: Optional[str] = Field(None, description="Target audience")
    numSlides: int = Field(10, ge=8, le=10, description="Number of slides (8-10)")
    keyThemes: List[str] = Field(default_factory=list, description="Key themes to cover")
    tone: Optional[str] = Field(None, description="Presentation tone")
    objectives: Optional[str] = Field(None, description="Presentation objectives")


class DataRequirements(BaseModel):
    """Data requirements model."""
    documentsRequested: List[str] = Field(default_factory=list, description="Requested documents")
    contentToExtract: List[str] = Field(default_factory=list, description="Content types to extract")
    metrics: List[str] = Field(default_factory=list, description="Metrics/KPIs")
    timePeriods: List[str] = Field(default_factory=list, description="Time periods")
    comparisons: List[str] = Field(default_factory=list, description="Comparison types")
    dataCategories: List[str] = Field(default_factory=list, description="Data categories")


class VisualPreferences(BaseModel):
    """Visual preferences model."""
    chartTypes: List[str] = Field(default_factory=list, description="Preferred chart types")
    style: Optional[str] = Field(None, description="Visual style")
    includeImages: Optional[bool] = Field(None, description="Include images")
    colorScheme: Optional[str] = Field(None, description="Color scheme")


class ExtractedInformation(BaseModel):
    """Extracted information model."""
    presentationRequirements: PresentationRequirements
    dataRequirements: DataRequirements
    visualPreferences: VisualPreferences


class DataMapping(BaseModel):
    """Data mapping for bullet points."""
    queryId: Optional[str] = Field(None, description="Query ID from RAG results")
    metricName: Optional[str] = Field(None, description="Metric name")
    dataType: Optional[str] = Field(None, description="Data type: metric, comparison, trend, insight")


class BulletPoint(BaseModel):
    """Bullet point model."""
    bulletText: str = Field(..., description="Main bullet point text")
    subBullets: Optional[List[str]] = Field(None, description="Sub-bullet points")
    requiresData: bool = Field(False, description="Whether bullet requires data")
    dataMapping: Optional[DataMapping] = Field(None, description="Data mapping information")


class VisualHint(BaseModel):
    """Visual hint model."""
    visualType: str = Field(..., description="Visual type: chart, table, image, icon, diagram")
    chartType: Optional[str] = Field(None, description="Chart type if visualType is chart")
    dataSource: str = Field(..., description="Query ID or metric name")
    purpose: Optional[str] = Field(None, description="Purpose of the visual")


class Slide(BaseModel):
    """Slide model."""
    slideNumber: int = Field(..., description="Slide number (1-indexed)")
    slideType: str = Field(..., description="Slide type")
    title: str = Field(..., description="Slide title")
    bulletPoints: List[BulletPoint] = Field(default_factory=list, description="Bullet points")
    visualHints: List[VisualHint] = Field(default_factory=list, description="Visual hints")
    speakerNotes: Optional[str] = Field(None, description="Speaker notes")
    keyMessage: str = Field(..., description="Main takeaway")


class PresentationOutline(BaseModel):
    """Presentation outline model."""
    title: str = Field(..., description="Presentation title")
    subtitle: Optional[str] = Field(None, description="Presentation subtitle")
    totalSlides: int = Field(..., ge=8, le=10, description="Total slides (8-10)")
    narrativeFlow: str = Field(..., description="Narrative flow description")
    slides: List[Slide] = Field(..., description="Slide array")


class GeneratedQueryFilters(BaseModel):
    """Filters for generated queries."""
    documents: Optional[List[str]] = Field(default_factory=list)
    time_periods: Optional[List[str]] = Field(default_factory=list)
    data_categories: Optional[List[str]] = Field(default_factory=list)
    metrics: Optional[List[str]] = Field(default_factory=list)
    comparisons: Optional[List[str]] = Field(default_factory=list)


class GeneratedQuery(BaseModel):
    """Generated query model."""
    query: str = Field(..., description="Query text")
    query_type: str = Field(..., description="Query type: metric, comparison, trend, insight")
    priority: str = Field(..., description="Priority: high, medium, low")
    filters: Optional[GeneratedQueryFilters] = Field(None, description="Query filters")
    rationale: Optional[str] = Field(None, description="Rationale for this query")


class LLMEnhancedAnswer(BaseModel):
    """LLM enhanced answer from Query Agent."""
    answer: str
    confidence: float
    extractedData: Dict[str, Any] = Field(default_factory=dict)


class QueryResult(BaseModel):
    """Query result model."""
    queryId: str
    generatedQuery: Optional[GeneratedQuery] = Field(None, description="Generated query metadata")
    llmEnhancedAnswer: LLMEnhancedAnswer


class PreviousOutlineInfo(BaseModel):
    """Previous outline information for editing."""
    outlineId: Optional[str] = None
    presentationOutline: Optional[PresentationOutline] = None


class EditingContext(BaseModel):
    """Editing context model."""
    isEditing: bool = Field(False, description="Whether in editing mode")
    previousOutline: Optional[PreviousOutlineInfo] = Field(None, description="Previous outline")
    targetSlideForEdit: Optional[int] = Field(None, description="Target slide number for editing")


class SynthesisMetadata(BaseModel):
    """Synthesis metadata."""
    chunks_processed: Optional[int] = Field(None, description="Number of chunks processed")
    themes_covered: Optional[int] = Field(None, description="Number of themes covered")
    confidence_score: Optional[float] = Field(None, description="Overall confidence score")


class SynthesizedContext(BaseModel):
    """Synthesized context from Query Agent."""
    synthesized_answers: Optional[Dict[str, Any]] = Field(None, description="Synthesized answers by theme")
    inter_query_insights: List[str] = Field(default_factory=list, description="Cross-query insights and patterns")
    data_quality_notes: Optional[List[str]] = Field(default_factory=list, description="Data quality observations")
    total_tokens_synthesized: Optional[int] = Field(None, description="Total tokens used in synthesis")
    synthesis_metadata: Optional[SynthesisMetadata] = Field(None, description="Synthesis metadata")


class PerformanceMetricsInput(BaseModel):
    """Performance metrics from Query Agent."""
    query_generation_time: Optional[float] = Field(None, description="Query generation time in seconds")
    retrieval_time: Optional[float] = Field(None, description="Retrieval time in seconds")
    synthesis_time: Optional[float] = Field(None, description="Synthesis time in seconds")
    total_tokens_retrieved: Optional[int] = Field(None, description="Total tokens retrieved")
    total_queries_generated: Optional[int] = Field(None, description="Total queries generated")


class OutlineGenerateRequest(BaseModel):
    """Request model for outline generation."""
    sessionId: str = Field(..., description="Session ID")
    userId: str = Field(..., description="User ID")
    extractedInformation: ExtractedInformation = Field(..., description="Extracted information")
    queryResults: List[QueryResult] = Field(..., description="Query results from RAG")
    synthesizedContext: Optional[SynthesizedContext] = Field(None, description="Synthesized context with inter-query insights")
    generatedQueries: Optional[List[GeneratedQuery]] = Field(default_factory=list, description="Generated queries metadata")
    performanceMetrics: Optional[PerformanceMetricsInput] = Field(None, description="Performance metrics from Query Agent")

    @validator('queryResults')
    def validate_query_results(cls, v):
        if not v:
            raise ValueError("queryResults cannot be empty")
        return v

    class Config:
        json_schema_extra = {
            "example": OUTLINE_GENERATE_EXAMPLE if OUTLINE_GENERATE_EXAMPLE else {
                "sessionId": "session_example_001",
                "userId": "user_example_001",
                "extractedInformation": {
                    "presentationRequirements": {
                        "topic": "Example Presentation Topic",
                        "targetAudience": "Executive Team",
                        "numSlides": 10,
                        "keyThemes": ["theme1", "theme2"],
                        "tone": "Professional",
                        "objectives": "Example objectives"
                    },
                    "dataRequirements": {
                        "documentsRequested": ["document1.pdf"],
                        "contentToExtract": ["metrics", "trends"],
                        "metrics": ["metric1", "metric2"],
                        "timePeriods": ["Q1 2024"],
                        "comparisons": ["QoQ"],
                        "dataCategories": ["financial"]
                    },
                    "visualPreferences": {
                        "chartTypes": ["line_chart", "bar_chart"],
                        "style": "Corporate",
                        "includeImages": True,
                        "colorScheme": "blue"
                    }
                },
                "queryResults": [
                    {
                        "queryId": "query_001",
                        "llmEnhancedAnswer": {
                            "answer": "Example answer with metrics and insights",
                            "confidence": 0.95,
                            "extractedData": {
                                "metrics": [
                                    {
                                        "metric_name": "Revenue",
                                        "value": "$100M",
                                        "context": "Q1 2024"
                                    }
                                ]
                            }
                        }
                    }
                ],
                "synthesizedContext": {
                    "synthesized_answers": {
                        "example_theme": {
                            "answer": "Synthesized answer combining multiple queries",
                            "key_points": ["Point 1", "Point 2"],
                            "confidence": "high"
                        }
                    },
                    "inter_query_insights": [
                        "Revenue growth is consistent across all quarters",
                        "Market trends indicate positive outlook"
                    ],
                    "data_quality_notes": [
                        "All data sources verified and complete"
                    ],
                    "total_tokens_synthesized": 500,
                    "synthesis_metadata": {
                        "chunks_processed": 10,
                        "themes_covered": 3,
                        "confidence_score": 0.92
                    }
                },
                "generatedQueries": [
                    {
                        "query": "What was the revenue in Q1 2024?",
                        "query_type": "metric",
                        "priority": "high",
                        "filters": {
                            "documents": ["document1.pdf"],
                            "time_periods": ["Q1 2024"],
                            "data_categories": ["financial"],
                            "metrics": ["revenue"]
                        },
                        "rationale": "Core financial metric for the period"
                    }
                ],
                "performanceMetrics": {
                    "query_generation_time": 2.5,
                    "retrieval_time": 5.3,
                    "synthesis_time": 3.8,
                    "total_tokens_retrieved": 10000,
                    "total_queries_generated": 5
                }
            }
        }


class OutlineEditRequest(BaseModel):
    """Request model for outline editing."""
    sessionId: str = Field(..., description="Session ID")
    userId: str = Field(..., description="User ID")
    previousOutline: PresentationOutline = Field(..., description="Previously generated outline to be edited")
    userFeedback: str = Field(..., description="User's edit request or feedback message")
    extractedInformation: ExtractedInformation = Field(..., description="Original/updated extracted information")
    queryResults: List[QueryResult] = Field(..., description="Query results from RAG (same as generation)")
    synthesizedContext: Optional[SynthesizedContext] = Field(None, description="Synthesized context with inter-query insights")
    generatedQueries: Optional[List[GeneratedQuery]] = Field(default_factory=list, description="Generated queries metadata")
    performanceMetrics: Optional[PerformanceMetricsInput] = Field(None, description="Performance metrics from Query Agent")
    targetSlideForEdit: Optional[int] = Field(None, description="Specific slide number to edit (1-indexed), or null for global edits")

    @validator('queryResults')
    def validate_query_results(cls, v):
        if not v:
            raise ValueError("queryResults cannot be empty")
        return v
    
    @validator('userFeedback')
    def validate_user_feedback(cls, v):
        if not v or not v.strip():
            raise ValueError("userFeedback cannot be empty")
        return v.strip()
    def validate_editing_context(cls, v):
        if not v.isEditing:
            raise ValueError("editingContext.isEditing must be True for editing")
        if not v.previousOutline:
            raise ValueError("editingContext.previousOutline is required for editing")
        return v


class DataIntegration(BaseModel):
    """Data integration metadata."""
    totalDataPoints: int
    queriesReferenced: List[str]
    coverageScore: float


class EditingMetadata(BaseModel):
    """Editing metadata."""
    modifiedSlides: List[int] = Field(default_factory=list)
    addedSlides: List[int] = Field(default_factory=list)
    removedSlides: List[int] = Field(default_factory=list)
    structuralChanges: Optional[str] = None


class OutlineMetadata(BaseModel):
    """Outline metadata."""
    templateCompliance: bool
    slideCountCompliance: bool
    narrativeCoherence: float
    dataIntegration: DataIntegration
    editingMetadata: Optional[EditingMetadata] = None


class QualityChecks(BaseModel):
    """Quality checks model."""
    allSlidesHaveTitles: bool
    bulletPointsWithinLimit: bool
    visualHintsProvided: bool
    dataBackedClaims: bool
    logicalFlow: bool


class PerformanceMetrics(BaseModel):
    """Performance metrics."""
    responseTime: float
    agentIterations: int
    toolCallsMade: int


class OutlineResponse(BaseModel):
    """Response model for outline operations."""
    success: bool
    sessionId: str
    userId: str
    outlineId: str
    cycleType: str
    presentationOutline: Optional[PresentationOutline] = None
    outlineMetadata: Optional[OutlineMetadata] = None
    qualityChecks: Optional[QualityChecks] = None
    nextAction: str
    handoffToAgent: Optional[str] = None
    performanceMetrics: PerformanceMetrics
    timestamp: str
    error: Optional[str] = None


# ===================== Global Agent Instance =====================

# Initialize agent (will be done in app startup)
outline_agent = None


def initialize_outline_agent(
    model_provider: str = "claude",
    model_name: str = "claude-sonnet-4-20250514",
    **kwargs
):
    """Initialize the global outline agent instance."""
    global outline_agent
    from src.agents.outline.agent import OutlineAgent
    
    outline_agent = OutlineAgent(
        model_provider=model_provider,
        model_name=model_name,
        **kwargs
    )
    logger.info("Outline Agent initialized successfully")


# ===================== API Endpoints =====================

@router.post(
    "/generate",
    response_model=OutlineResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Presentation Outline",
    description="Generate a new 8-10 slide presentation outline based on requirements and RAG results"
)
async def generate_outline(request: OutlineGenerateRequest) -> OutlineResponse:
    """
    Generate a new presentation outline.
    
    This endpoint takes presentation requirements and query results from the RAG engine
    and generates a structured 8-10 slide outline with:
    - Logical narrative flow
    - Data-backed bullet points
    - Visual suggestions
    - Compliance validation
    
    **Workflow:**
    1. Analyze requirements and preferences
    2. Process query results
    3. Generate outline structure
    4. Validate compliance and quality
    
    **Response Time Target:** <2 seconds
    """
    if not outline_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Outline Agent not initialized"
        )
    
    try:
        logger.info(f"Generating outline for session: {request.sessionId}")
        
        # Generate unique outline ID
        outline_id = f"outline_{uuid4().hex[:12]}"
        
        # Convert Pydantic models to dicts
        extracted_info = request.extractedInformation.dict()
        query_results = [qr.dict() for qr in request.queryResults]

        # Include optional fields if present
        synthesized_context = request.synthesizedContext.dict() if request.synthesizedContext else None
        generated_queries = [gq.dict() for gq in request.generatedQueries] if request.generatedQueries else []
        performance_metrics = request.performanceMetrics.dict() if request.performanceMetrics else None

        # Run agent
        result = outline_agent.run(
            session_id=request.sessionId,
            user_id=request.userId,
            outline_id=outline_id,
            cycle_type="generation",
            extracted_information=extracted_info,
            query_results=query_results,
            editing_context=None,
            synthesized_context=synthesized_context,
            generated_queries=generated_queries,
            performance_metrics=performance_metrics
        )
        
        # Convert to response model
        response = OutlineResponse(**result)
        
        if not response.success:
            logger.error(f"Outline generation failed: {response.error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error or "Outline generation failed"
            )
        
        logger.info(
            f"Outline generated successfully: {outline_id} "
            f"({response.performanceMetrics.responseTime:.2f}s)"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_outline endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/edit",
    response_model=OutlineResponse,
    status_code=status.HTTP_200_OK,
    summary="Edit Presentation Outline",
    description="Edit an existing presentation outline based on user feedback"
)
async def edit_outline(
    request: OutlineEditRequest = Body(
        ...,
        openapi_examples=OUTLINE_EDIT_EXAMPLES if OUTLINE_EDIT_EXAMPLES else None
    )
) -> OutlineResponse:
    """
    Edit an existing presentation outline based on user feedback.
    
    This endpoint takes:
    - **previousOutline**: The outline generated from /outline/generate
    - **userFeedback**: User's edit request (e.g., "Make slide 5 more concise", "Add more data to slide 3")
    - **extractedInformation**: Original presentation requirements
    - **queryResults**: Same RAG results from generation
    - **targetSlideForEdit**: (Optional) Specific slide number to focus on
    
    **Editing Capabilities:**
    - Modify specific slides or entire outline
    - Update bullet points and data mappings
    - Change visual hints and speaker notes
    - Restructure slides while maintaining 8-10 slide limit
    - Track all changes in editingMetadata
    
    **Response Time Target:** <2 seconds
    """
    if not outline_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Outline Agent not initialized"
        )
    
    try:
        logger.info(
            f"Editing outline for session: {request.sessionId}, "
            f"user feedback: {request.userFeedback[:100]}..., "
            f"target slide: {request.targetSlideForEdit or 'global'}"
        )
        
        # Generate new outline ID for the edited version
        outline_id = f"outline_{uuid4().hex[:12]}"
        
        # Convert Pydantic models to dicts
        extracted_info = request.extractedInformation.dict()
        query_results = [qr.dict() for qr in request.queryResults]
        previous_outline = request.previousOutline.dict()
        
        # Build editing context
        editing_context = {
            "isEditing": True,
            "previousOutline": {
                "outlineId": outline_id,  # Will be updated in response
                "presentationOutline": previous_outline
            },
            "targetSlideForEdit": request.targetSlideForEdit,
            "userFeedback": request.userFeedback  # Add user feedback to context
        }
        
        # Optional fields
        synthesized_context = request.synthesizedContext.dict() if request.synthesizedContext else None
        generated_queries = [gq.dict() for gq in request.generatedQueries] if request.generatedQueries else None
        performance_metrics = request.performanceMetrics.dict() if request.performanceMetrics else None
        
        # Run agent in editing mode
        result = outline_agent.run(
            session_id=request.sessionId,
            user_id=request.userId,
            outline_id=outline_id,
            cycle_type="editing",
            extracted_information=extracted_info,
            query_results=query_results,
            editing_context=editing_context,
            synthesized_context=synthesized_context,
            generated_queries=generated_queries,
            performance_metrics=performance_metrics
        )
        
        # Convert to response model
        response = OutlineResponse(**result)
        
        if not response.success:
            logger.error(f"Outline editing failed: {response.error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error or "Outline editing failed"
            )
        
        logger.info(
            f"Outline edited successfully: {outline_id} "
            f"({response.performanceMetrics.responseTime:.2f}s), "
            f"modified slides: {response.outlineMetadata.editingMetadata.modifiedSlides if response.outlineMetadata and response.outlineMetadata.editingMetadata else 'none'}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in edit_outline endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if Outline Agent is initialized and ready"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for Outline Agent.
    
    Returns:
        Status information about the agent
    """
    return {
        "status": "healthy" if outline_agent else "not_initialized",
        "agent_initialized": outline_agent is not None,
        "timestamp": datetime.now().isoformat()
    }


# ===================== Optional: Validation Endpoint =====================

@router.post(
    "/validate",
    status_code=status.HTTP_200_OK,
    summary="Validate Outline",
    description="Validate an outline for quality and compliance without regenerating"
)
async def validate_outline_endpoint(
    outline: PresentationOutline,
    requirements: ExtractedInformation
) -> Dict[str, Any]:
    """
    Validate an outline for quality and compliance.
    
    This endpoint performs validation checks without modifying the outline:
    - Template compliance (8-10 slides)
    - Data integrity (all claims mapped)
    - Narrative coherence
    - Visual planning
    - Quality standards
    """
    if not outline_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Outline Agent not initialized"
        )
    
    try:
        # Use the agent's validation tool
        validation_input = {
            "outline": outline.dict(),
            "requirements": requirements.dict()
        }
        
        result = outline_agent._validate_outline(str(validation_input))
        validation_data = eval(result)  # Convert string to dict
        
        return {
            "success": True,
            "validation": validation_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in validate_outline endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}"
        )