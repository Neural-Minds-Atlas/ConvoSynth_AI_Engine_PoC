"""
FastAPI routes for Image Coordination Agent
"""

from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
from datetime import datetime
import json

from src.agents.image_coordination.agent import (
    ImageCoordinationAgent,
    ImageCoordinationInput,
    ImageCoordinationOutput,
    VisualElement,
    DataPoint,
    create_image_coordination_agent
)


# Create router
router = APIRouter(
    prefix="/api/agents/image-coordination",
    tags=["Image Coordination Agent"]
)


# Example payload for Swagger UI
EXAMPLE_PAYLOAD = {
    "presentation_id": "pres_12345",
    "user_id": "user_67890",
    "id": "req-xyz-001",
    "session_id": "sess-abc-001",
    "visualElements": [
        {
            "visualType": "chart",
            "chartType": "bar_chart",
            "dataSource": "BDX Stock Historical Prices & Data - Yahoo Finance",
            "dataValue": "Monthly average closing prices and trading volumes for July-September 2025",
            "purpose": "Visual representation of two-month timeline showing BDX stock performance trends and trading activity to support risk vs rebound analysis",
            "xAxisLabel": "Month",
            "yAxisLabel": "Average Closing Price (USD) / Volume (Millions)",
            "title": "BDX Two-Month Performance Overview: July-September 2025",
            "dataPoints": [
                {
                    "x": "July 2025",
                    "y": 176.85,
                    "label": "July Avg Price",
                    "category": "price",
                    "volume": 3.2
                },
                {
                    "x": "August 2025",
                    "y": 190.45,
                    "label": "August Avg Price",
                    "category": "price",
                    "volume": 2.4
                },
                {
                    "x": "September 2025",
                    "y": 189.12,
                    "label": "September Avg Price",
                    "category": "price",
                    "volume": 1.6
                }
            ],
            "colorScheme": "Corporate blue (#1f4e79) for prices, corporate green (#2d5016) for volume bars",
            "annotations": [
                "Recovery from July lows ($172-$180 range)",
                "Peak volatility in August ($172-$200 range)",
                "Dividend payment Sept 8: $1.04",
                "Current price: $186.84 (-1.95%)",
                "Volume declining trend indicates stabilization"
            ]
        },
        {
            "visualType": "chart",
            "chartType": "line_chart",
            "dataSource": "volatility_analysis_sep",
            "dataValue": "Daily price volatility (High-Low range) for BDX stock comparing August and September 2025",
            "purpose": "Compare volatility trends between August and September to assess market stability and risk patterns",
            "xAxisLabel": "Date",
            "yAxisLabel": "Daily Volatility (USD)",
            "title": "BDX Stock Volatility Comparison: August vs September 2025",
            "dataPoints": [
                {
                    "x": "2025-08-05",
                    "y": 3.57,
                    "label": "Aug 5",
                    "month": "August"
                },
                {
                    "x": "2025-08-06",
                    "y": 5.19,
                    "label": "Aug 6",
                    "month": "August"
                },
                {
                    "x": "2025-08-07",
                    "y": 5.91,
                    "label": "Aug 7",
                    "month": "August"
                },
                {
                    "x": "2025-08-08",
                    "y": 7.01,
                    "label": "Aug 8",
                    "month": "August"
                },
                {
                    "x": "2025-08-11",
                    "y": 3.9,
                    "label": "Aug 11",
                    "month": "August"
                },
                {
                    "x": "2025-08-12",
                    "y": 2.6,
                    "label": "Aug 12",
                    "month": "August"
                },
                {
                    "x": "2025-08-13",
                    "y": 2.33,
                    "label": "Aug 13",
                    "month": "August"
                },
                {
                    "x": "2025-08-14",
                    "y": 2.17,
                    "label": "Aug 14",
                    "month": "August"
                },
                {
                    "x": "2025-08-15",
                    "y": 2.35,
                    "label": "Aug 15",
                    "month": "August"
                },
                {
                    "x": "2025-08-18",
                    "y": 2.46,
                    "label": "Aug 18",
                    "month": "August"
                },
                {
                    "x": "2025-08-19",
                    "y": 3.99,
                    "label": "Aug 19",
                    "month": "August"
                },
                {
                    "x": "2025-08-20",
                    "y": 2.75,
                    "label": "Aug 20",
                    "month": "August"
                },
                {
                    "x": "2025-08-21",
                    "y": 2.48,
                    "label": "Aug 21",
                    "month": "August"
                },
                {
                    "x": "2025-08-22",
                    "y": 2.97,
                    "label": "Aug 22",
                    "month": "August"
                },
                {
                    "x": "2025-08-25",
                    "y": 5.45,
                    "label": "Aug 25",
                    "month": "August"
                },
                {
                    "x": "2025-08-26",
                    "y": 1.73,
                    "label": "Aug 26",
                    "month": "August"
                },
                {
                    "x": "2025-08-27",
                    "y": 2.01,
                    "label": "Aug 27",
                    "month": "August"
                },
                {
                    "x": "2025-08-28",
                    "y": 4.56,
                    "label": "Aug 28",
                    "month": "August"
                },
                {
                    "x": "2025-08-29",
                    "y": 2.04,
                    "label": "Aug 29",
                    "month": "August"
                },
                {
                    "x": "2025-09-02",
                    "y": 5.96,
                    "label": "Sep 2",
                    "month": "September"
                },
                {
                    "x": "2025-09-03",
                    "y": 5.89,
                    "label": "Sep 3",
                    "month": "September"
                },
                {
                    "x": "2025-09-04",
                    "y": 4.28,
                    "label": "Sep 4",
                    "month": "September"
                },
                {
                    "x": "2025-09-05",
                    "y": 2.15,
                    "label": "Sep 5",
                    "month": "September"
                },
                {
                    "x": "2025-09-08",
                    "y": 4.08,
                    "label": "Sep 8",
                    "month": "September"
                },
                {
                    "x": "2025-09-09",
                    "y": 2.13,
                    "label": "Sep 9",
                    "month": "September"
                },
                {
                    "x": "2025-09-10",
                    "y": 3,
                    "label": "Sep 10",
                    "month": "September"
                },
                {
                    "x": "2025-09-11",
                    "y": 3.17,
                    "label": "Sep 11",
                    "month": "September"
                },
                {
                    "x": "2025-09-12",
                    "y": 3.06,
                    "label": "Sep 12",
                    "month": "September"
                }
            ],
            "colorScheme": "Corporate blue for August trend, corporate green for September trend",
            "annotations": [
                "Peak volatility on Aug 8 ($7.01 range)",
                "High volatility period: early August",
                "September shows more moderate volatility",
                "Average August volatility: $3.42",
                "Average September volatility: $3.64",
                "Volatility spike on Sep 2-3 following month transition"
            ]
        }
    ]
}


# Global agent instance (initialized on first request)
_agent_instance: ImageCoordinationAgent = None


def get_agent() -> ImageCoordinationAgent:
    """
    Get or create the Image Coordination Agent instance.
    Uses lazy initialization.
    """
    global _agent_instance
    
    if _agent_instance is None:
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        _agent_instance = create_image_coordination_agent(
            anthropic_api_key=anthropic_api_key,
            model_name="claude-sonnet-4-20250514",
            temperature=0.3,
            max_tokens=4096,
            verbose=True
        )
    
    return _agent_instance


# ==================== HEALTH CHECK ====================

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint for Image Coordination Agent.
    """
    return {
        "status": "healthy",
        "agent": "Image Coordination Agent",
        "model": "claude-sonnet-4-20250514",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# ==================== MAIN ENDPOINT ====================

@router.post("/generate-charts", response_model=ImageCoordinationOutput)
async def generate_charts(input_data: ImageCoordinationInput = Body(..., example=EXAMPLE_PAYLOAD)):
    """
    Generate Chart.js configurations from visual element specifications.
    
    **Request Body:**
    - `session_id` (string): Session identifier
    - `id` (string): Unique request identifier
    - `presentation_id` (string, optional): Presentation identifier
    - `user_id` (string, optional): User identifier
    - `visualElements` (array): Array of visual element specifications
    
    **Visual Element Schema:**
    - `visualType` (string): Type of visual (e.g., "chart")
    - `chartType` (string): Chart type - "bar_chart", "line_chart", "pie_chart", "area_chart"
    - `dataSource` (string): Source of the data
    - `dataValue` (string): Description of data values
    - `purpose` (string): Purpose of the visualization
    - `xAxisLabel` (string): Label for X-axis
    - `yAxisLabel` (string): Label for Y-axis
    - `title` (string): Chart title
    - `dataPoints` (array): Array of data points with x, y, label, category, volume
    - `colorScheme` (string): Color scheme description (can include hex codes)
    - `annotations` (array): Additional annotations/notes
    
    **Response:**
    - `session_id` (string): Session identifier
    - `id` (string): Request identifier
    - `presentation_id` (string, optional): Presentation identifier
    - `user_id` (string, optional): User identifier
    - `generatedCharts` (array): Array of Chart.js configurations
    - `chartCount` (integer): Number of charts generated
    - `timestamp` (string): Generation timestamp
    
    **Chart Output Schema:**
    Each generated chart contains:
    - `id` (string): Unique chart identifier
    - `cfg` (object): Complete Chart.js configuration
    - `exportScale` (float): Export scale factor (0.7)
    """
    try:
        # Get agent instance
        agent = get_agent()
        
        # Validate input
        if not input_data.visualElements:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No visual elements provided"
            )
        
        # Process visual elements
        output = agent.process(input_data)
        
        # Return response
        return output
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chart generation failed: {str(e)}"
        )


# ==================== DIRECT TOOL ENDPOINT (FOR TESTING) ====================

@router.post("/generate-single-chart")
async def generate_single_chart(visual_element: VisualElement):
    """
    Generate a single Chart.js configuration directly (bypasses agent).
    Useful for testing and debugging.
    
    **Request Body:**
    Single visual element specification (same schema as visualElements array item)
    
    **Response:**
    Single Chart.js configuration object
    """
    try:
        from src.agents.image_coordination.agent import generate_chart_config_tool

        result = generate_chart_config_tool(visual_element.model_dump())
        
        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=result["chart_config"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chart generation failed: {str(e)}"
        )


# ==================== BATCH ENDPOINT ====================

@router.post("/generate-charts-batch")
async def generate_charts_batch(
    requests: List[ImageCoordinationInput]
):
    """
    Batch endpoint for generating multiple chart sets in a single request.
    
    **Request Body:**
    Array of ImageCoordinationInput objects
    
    **Response:**
    Array of ImageCoordinationOutput objects
    """
    try:
        agent = get_agent()
        
        results = []
        for req in requests:
            try:
                output = agent.process(req)
                results.append({
                    "success": True,
                    "id": req.id,
                    "output": output.model_dump()
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "id": getattr(req, "id", None),
                    "error": str(e)
                })
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"results": results}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {str(e)}"
        )


# ==================== VALIDATION ENDPOINT ====================

@router.post("/validate-chart-config")
async def validate_chart_config(chart_config: Dict[str, Any]):
    """
    Validate a Chart.js configuration for correctness and completeness.
    
    **Request Body:**
    Chart.js configuration object to validate
    
    **Response:**
    Validation result with issues and suggestions
    """
    try:
        issues = []
        suggestions = []
        
        # Check required top-level fields
        if "id" not in chart_config:
            issues.append("Missing required field: id")
        if "cfg" not in chart_config:
            issues.append("Missing required field: cfg")
            return {"valid": False, "issues": issues, "suggestions": ["Add 'cfg' object"]}
        
        cfg = chart_config["cfg"]
        
        # Check required cfg fields
        if "type" not in cfg:
            issues.append("Missing required field: cfg.type")
        elif cfg["type"] not in ["bar", "line", "pie"]:
            issues.append(f"Invalid chart type: {cfg['type']}")
        
        if "data" not in cfg:
            issues.append("Missing required field: cfg.data")
        else:
            data = cfg["data"]
            if "labels" not in data:
                issues.append("Missing required field: cfg.data.labels")
            if "datasets" not in data:
                issues.append("Missing required field: cfg.data.datasets")
            elif not isinstance(data["datasets"], list) or len(data["datasets"]) == 0:
                issues.append("cfg.data.datasets must be a non-empty array")
        
        if "options" not in cfg:
            issues.append("Missing required field: cfg.options")
        else:
            options = cfg["options"]
            if "plugins" not in options:
                issues.append("Missing required field: cfg.options.plugins")
        
        # Provide suggestions if there are issues
        if issues:
            suggestions.append("Ensure all required fields are present")
            suggestions.append("Validate chart type is one of: bar, line, pie")
            suggestions.append("Check that data.labels and data.datasets are properly formatted")
        
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues if issues else [],
            "suggestions": suggestions if suggestions else ["Configuration looks good!"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


# ==================== EXAMPLE PAYLOADS ====================

@router.get("/examples")
async def get_example_payloads():
    """
    Get example request payloads for testing.
    
    Returns various example scenarios:
    - Single bar chart
    - Multiple charts (bar, line, pie)
    - Area chart
    - Financial data visualization
    """
    return {
        "single_bar_chart": {
            "session_id": "session-123",
            "id": "req-001",
            "visualElements": [
                {
                    "visualType": "chart",
                    "chartType": "bar_chart",
                    "dataSource": "Sample Data",
                    "dataValue": "Monthly sales figures",
                    "purpose": "Show sales trend",
                    "xAxisLabel": "Month",
                    "yAxisLabel": "Sales ($)",
                    "title": "Monthly Sales Performance",
                    "dataPoints": [
                        {"x": "Jan", "y": 15000, "label": "January Sales", "category": "sales"},
                        {"x": "Feb", "y": 18000, "label": "February Sales", "category": "sales"},
                        {"x": "Mar", "y": 22000, "label": "March Sales", "category": "sales"}
                    ],
                    "colorScheme": "Corporate blue (#2376DD) for bars",
                    "annotations": ["Q1 Performance", "Upward trend observed"]
                }
            ]
        },
        "multiple_charts": {
            "session_id": "session-456",
            "id": "req-002",
            "visualElements": [
                {
                    "visualType": "chart",
                    "chartType": "bar_chart",
                    "dataSource": "Revenue Data",
                    "dataValue": "Quarterly revenue",
                    "purpose": "Show revenue distribution",
                    "xAxisLabel": "Quarter",
                    "yAxisLabel": "Revenue ($M)",
                    "title": "Quarterly Revenue Breakdown",
                    "dataPoints": [
                        {"x": "Q1", "y": 125, "label": "Q1 Revenue", "category": "revenue"},
                        {"x": "Q2", "y": 145, "label": "Q2 Revenue", "category": "revenue"},
                        {"x": "Q3", "y": 132, "label": "Q3 Revenue", "category": "revenue"},
                        {"x": "Q4", "y": 168, "label": "Q4 Revenue", "category": "revenue"}
                    ],
                    "colorScheme": "#2376DD, #10B981, #F59E0B, #EF4444",
                    "annotations": []
                },
                {
                    "visualType": "chart",
                    "chartType": "line_chart",
                    "dataSource": "User Growth Data",
                    "dataValue": "Monthly active users",
                    "purpose": "Track user growth",
                    "xAxisLabel": "Month",
                    "yAxisLabel": "Users (K)",
                    "title": "User Growth Trend",
                    "dataPoints": [
                        {"x": "Jan", "y": 45, "label": "January Users", "category": "users"},
                        {"x": "Feb", "y": 52, "label": "February Users", "category": "users"},
                        {"x": "Mar", "y": 58, "label": "March Users", "category": "users"},
                        {"x": "Apr", "y": 67, "label": "April Users", "category": "users"}
                    ],
                    "colorScheme": "Growth green (#10B981)",
                    "annotations": ["Consistent growth"]
                },
                {
                    "visualType": "chart",
                    "chartType": "pie_chart",
                    "dataSource": "Market Share Data",
                    "dataValue": "Market distribution",
                    "purpose": "Show market share",
                    "xAxisLabel": "",
                    "yAxisLabel": "",
                    "title": "Market Share Distribution",
                    "dataPoints": [
                        {"x": "Product A", "y": 35, "label": "Product A", "category": "market"},
                        {"x": "Product B", "y": 25, "label": "Product B", "category": "market"},
                        {"x": "Product C", "y": 40, "label": "Product C", "category": "market"}
                    ],
                    "colorScheme": "#2376DD, #10B981, #F59E0B",
                    "annotations": ["Product C leads"]
                }
            ]
        },
        "financial_data": {
            "session_id": "session-789",
            "id": "req-003",
            "visualElements": [
                {
                    "visualType": "chart",
                    "chartType": "bar_chart",
                    "dataSource": "BDX Stock Historical Prices & Data - Yahoo Finance",
                    "dataValue": "Monthly average closing prices and trading volumes for July-September 2025",
                    "purpose": "Visual representation of two-month timeline showing BDX stock performance trends and trading activity",
                    "xAxisLabel": "Month",
                    "yAxisLabel": "Average Closing Price (USD)",
                    "title": "BDX Two-Month Performance Overview: July-September 2025",
                    "dataPoints": [
                        {"x": "July 2025", "y": 176.85, "label": "July Avg Price", "category": "price", "volume": 3.2},
                        {"x": "August 2025", "y": 190.45, "label": "August Avg Price", "category": "price", "volume": 2.4},
                        {"x": "September 2025", "y": 189.12, "label": "September Avg Price", "category": "price", "volume": 1.6}
                    ],
                    "colorScheme": "Corporate blue (#1f4e79) for prices, corporate green (#2d5016) for volume bars",
                    "annotations": [
                        "Recovery from July lows ($172-$180 range)",
                        "Peak volatility in August ($172-$200 range)",
                        "Current price: $186.84 (-1.95%)"
                    ]
                }
            ]
        }
    }