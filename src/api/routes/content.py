"""
Content Agent FastAPI Routes
API endpoints for content generation
"""

import os
import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.responses import JSONResponse

from src.agents.content.agent import ContentAgent
from src.agents.content.models import ContentAgentInput, ContentAgentOutput
from .content_example_payload import CONTENT_GENERATE_EXAMPLE
from src.db.mongodb import get_collection 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/content",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

# Initialize Content Agent (will be done in lifespan)
content_agent: ContentAgent = None


def get_content_agent() -> ContentAgent:
    """Dependency to get content agent instance"""
    if content_agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Content Agent not initialized"
        )
    return content_agent


def initialize_content_agent(rag_client=None):
    """Initialize the content agent with API keys from environment"""
    global content_agent

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    content_agent = ContentAgent(
        anthropic_api_key=anthropic_api_key,
        rag_client=rag_client,
        model_name="claude-sonnet-4-20250514",
        temperature=0.3,
        max_tokens=4096
    )

    logger.info("Content Agent initialized successfully")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post(
    "/generate",
    response_model=ContentAgentOutput,
    status_code=status.HTTP_200_OK,
    summary="Generate Expanded Content",
    description="""
    Generate comprehensive content for presentation slides by expanding the outline.
    
    This endpoint:
    1. Receives extracted information from Conversation Agent
    2. Receives outline from Outline Agent
    3. Queries RAG system for detailed data
    4. Expands bullet points into full content
    5. Generates complete visual element specifications
    6. Creates comprehensive speaker notes
    
    **Performance Target**: <4 seconds response time
    **Accuracy Target**: 95% financial accuracy
    **LLM**: Claude-4 Sonnet
    """,
    responses={
        200: {
            "description": "Content generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "sessionId": "session_bdx_stock_analysis_001",
                        "userId": "user_portfolio_manager_123",
                        "contentId": "content_1696084225",
                        "cycleType": "generate",
                        "expandedPresentationContent": {
                            "title": "BDX Stock Performance Analysis: August-September 2025 Comparison",
                            "subtitle": "Comprehensive Price Movement and Volatility Assessment",
                            "totalSlides": 10,
                            "slides": [
                                {
                                    "slideNumber": 1,
                                    "slideType": "title",
                                    "title": "BDX Stock Performance Analysis",
                                    "bulletPoints": [
                                        {
                                            "bulletTextContent": "This presentation provides a comprehensive comparison of BDX stock performance between August and September 2025, analyzing price movements, volatility patterns, and trading behavior to deliver actionable insights for investment decision-making.",
                                            "subBulletsContent": [
                                                "Detailed analysis of daily price movements, identifying key trends and inflection points across both months",
                                                "Comprehensive volatility assessment measuring risk levels and market sentiment shifts during the period"
                                            ],
                                            "requiresData": False,
                                            "dataMapping": []
                                        }
                                    ],
                                    "visualElements": [
                                        {
                                            "visualType": "image",
                                            "chartType": None,
                                            "dataSource": "Company logo and stock ticker",
                                            "dataValue": "BDX logo with NYSE ticker symbol",
                                            "purpose": "Professional branding and immediate recognition",
                                            "colorScheme": "Corporate blue and green with accent colors"
                                        }
                                    ],
                                    "speakerNotes": "Welcome the investment committee to this comprehensive analysis...",
                                    "keyMessage": "Professional introduction to BDX stock performance analysis"
                                }
                            ]
                        },
                        "contentMetadata": {
                            "slideCountCompliance": True,
                            "narrativeCoherence": 0.95,
                            "dataIntegration": {
                                "totalDataPoints": 45,
                                "queriesReferenced": ["query_0", "query_1", "query_2"],
                                "coverageScore": 0.92
                            },
                            "ragQueriesMade": 12,
                            "dataPointsExtracted": 45,
                            "citationsAdded": 45
                        },
                        "qualityChecks": {
                            "allSlidesHaveTitles": True,
                            "bulletPointsWithinLimit": True,
                            "visualElementsProvided": True,
                            "dataBackedClaims": True,
                            "logicalFlow": True,
                            "financialAccuracy": 0.97
                        },
                        "nextAction": "proceed_to_qa_agent",
                        "handoffToAgent": "qa_agent",
                        "performanceMetrics": {
                            "responseTime": 3.45,
                            "agentIterations": 10,
                            "toolCallsMade": 35
                        },
                        "timestamp": "2025-09-30T14:25:30.123Z",
                        "error": None
                    }
                }
            }
        },
        400: {"description": "Invalid input data"},
        503: {"description": "Content Agent not available"},
        500: {"description": "Internal server error"}
    }
)
async def generate_content(
    input_data: ContentAgentInput = Body(..., openapi_examples={
        "bdx_stock_analysis": {
            "summary": "BDX Stock Analysis Example (Complete with all 10 slides)",
            "description": "Full example showing BDX stock performance analysis across August-September 2025 with complete slide data",
            "value": CONTENT_GENERATE_EXAMPLE
        }
    }),
    agent: ContentAgent = Depends(get_content_agent)
) -> ContentAgentOutput:
    """
    Generate expanded presentation content

    Args:
        input_data: Complete input including extracted information and outline
        agent: Content Agent instance (injected)

    Returns:
        Expanded presentation content with all details
    """
    try:
        logger.info(f"Received content generation request for session: {input_data.sessionId}")

        # Validate input
        if not input_data.outlineAgentOutput.presentationOutline.slides:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No slides found in outline"
            )

        # Generate content (now async)
        result = await agent.generate_content(input_data)

        logger.info(f"Content generation completed: {result.success}")

        # Save Content Agent output to MongoDB
        try:
            from datetime import datetime
            content_collection = get_collection("content_outputs")

            # Convert to dict for MongoDB with camelCase aliases
            content_dict = result.model_dump(by_alias=True, exclude_none=False)

            # Add createdAt timestamp for MongoDB
            content_dict["createdAt"] = datetime.utcnow()

            logger.info(f"Saving content to MongoDB: content_id={result.contentId}, session_id={result.sessionId}")

            # Save to MongoDB
            await content_collection.insert_one(content_dict)

            logger.info(f"Content saved to MongoDB: content_id={result.contentId}, session_id={result.sessionId}")

        except Exception as e:
            logger.error(f"Failed to save content to MongoDB: {str(e)}", exc_info=True)
            # Don't fail the request if MongoDB save fails, just log the error

        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if Content Agent is healthy and ready"
)
async def health_check(agent: ContentAgent = Depends(get_content_agent)) -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "ContentAgent",
        "model": "claude-sonnet-4-20250514",
        "rag_client_available": agent.rag_client is not None
    }


@router.post(
    "/test",
    status_code=status.HTTP_200_OK,
    summary="Test Content Agent",
    description="Test endpoint with minimal data to verify agent functionality"
)
async def test_content_agent(agent: ContentAgent = Depends(get_content_agent)) -> Dict[str, Any]:
    """
    Simple test endpoint to verify agent is working
    """
    return {
        "status": "operational",
        "agent": "ContentAgent",
        "capabilities": [
            "Content expansion",
            "RAG integration",
            "Visual element specification",
            "Speaker notes generation",
            "Financial data extraction"
        ],
        "performance_targets": {
            "response_time": "<4 seconds",
            "financial_accuracy": "95%",
            "model": "claude-sonnet-4-20250514"
        }
    }


# ============================================================================
# STARTUP/SHUTDOWN HANDLERS
# ============================================================================

async def startup_event():
    """Initialize Content Agent on startup"""
    try:
        initialize_content_agent()
        logger.info("Content Agent service started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Content Agent: {str(e)}")
        raise


async def shutdown_event():
    """Cleanup on shutdown"""
    global content_agent
    if content_agent:
        del content_agent
        content_agent = None
    logger.info("Content Agent service shut down")


# Export for main app
__all__ = ["router", "startup_event", "shutdown_event", "initialize_content_agent"]