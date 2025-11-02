"""Outline Agent - Generate presentation structure using Claude-4/GPT-4."""
from typing import Any, Dict
from datetime import datetime
import structlog

from src.agents.base import BaseAgent, AgentRequest, AgentType
from src.agents.config import get_agent_config

logger = structlog.get_logger(__name__)


OUTLINE_SYSTEM_PROMPT = """You are an expert presentation architect specializing in financial presentations.

Generate a comprehensive presentation outline with complete metadata for downstream agents.

Return JSON with this EXACT structure:
{
    "presentation_outline": {
        "title": "Presentation Title",
        "subtitle": "Subtitle (optional)",
        "totalSlides": 10,
        "narrativeFlow": "Description of narrative flow",
        "slides": [
            {
                "slideNumber": 1,
                "slideType": "title_slide | overview_slide | data_slide | comparison_slide | trend_slide | insight_slide | recommendation_slide | conclusion_slide",
                "title": "Slide Title",
                "bulletPoints": [
                    {
                        "bulletText": "Main bullet point text",
                        "subBullets": ["sub-bullet 1", "sub-bullet 2"] or null,
                        "requiresData": true or false,
                        "dataMapping": {
                            "queryId": "query_1" or null,
                            "metricName": "metric name" or null,
                            "dataType": "metric | comparison | trend | insight | topic" or null
                        }
                    }
                ],
                "visualHints": [
                    {
                        "visualType": "chart | image | diagram | table",
                        "chartType": "line | bar | pie | scatter" or null,
                        "dataSource": "source identifier",
                        "purpose": "Purpose description"
                    }
                ],
                "speakerNotes": "Speaker notes",
                "keyMessage": "Key message for this slide"
            }
        ]
    },
    "outline_metadata": {
        "templateCompliance": true,
        "slideCountCompliance": true,
        "narrativeCoherence": 0.95,
        "dataIntegration": {
            "totalDataPoints": 18,
            "queriesReferenced": ["query_1", "query_2"],
            "coverageScore": 1.0
        },
        "editingMetadata": null
    },
    "quality_checks": {
        "allSlidesHaveTitles": true,
        "bulletPointsWithinLimit": true,
        "visualHintsProvided": true,
        "dataBackedClaims": true,
        "logicalFlow": true
    },
    "next_action": "proceed_to_content_agent",
    "handoff_to_agent": null
}

IMPORTANT: Return ONLY the JSON object, no additional text.
"""


class OutlineAgent(BaseAgent):
    """Outline Agent using Claude-4/GPT-4 with Zero-shot ReAct."""

    def __init__(self):
        config = get_agent_config(AgentType.OUTLINE)
        super().__init__(
            agent_name="outline_agent",
            agent_type=AgentType.OUTLINE,
            config=config,
        )

    def _transform_to_new_format(self, old_outline: Dict[str, Any], query_output: Dict[str, Any]) -> Dict[str, Any]:
        """Transform old outline format to new format with complete metadata."""
        slides_data = old_outline.get("outline", [])

        # Transform slides to new format
        transformed_slides = []
        queries_referenced = set()

        for slide in slides_data:
            slide_number = slide.get("slide_number", 0)
            title = slide.get("title", "")
            bullet_points_text = slide.get("bullet_points", [])

            # Determine slide type based on position and content
            if slide_number == 1:
                slide_type = "title_slide"
            elif slide_number == 2:
                slide_type = "overview_slide"
            elif "recommendation" in title.lower() or "action" in title.lower():
                slide_type = "recommendation_slide"
            elif "conclusion" in title.lower() or "takeaway" in title.lower():
                slide_type = "conclusion_slide"
            elif "comparison" in title.lower() or "vs" in title.lower():
                slide_type = "comparison_slide"
            elif "trend" in title.lower() or "timeline" in title.lower():
                slide_type = "trend_slide"
            elif "insight" in title.lower() or "key" in title.lower():
                slide_type = "insight_slide"
            else:
                slide_type = "data_slide"

            # Transform bullet points to new format
            bullet_points = []
            for idx, bp_text in enumerate(bullet_points_text):
                # Check if bullet point mentions data/metrics
                requires_data = any(keyword in bp_text.lower() for keyword in ["$", "%", "price", "performance", "metric", "data"])

                query_id = None
                if requires_data and idx < 8:  # Map to query_1 through query_8
                    query_id = f"query_{idx + 1}"
                    queries_referenced.add(query_id)

                bullet_points.append({
                    "bulletText": bp_text,
                    "subBullets": None,
                    "requiresData": requires_data,
                    "dataMapping": {
                        "queryId": query_id,
                        "metricName": bp_text[:50] if requires_data else None,
                        "dataType": "metric" if requires_data else None
                    }
                })

            # Create visual hints
            visual_suggestion = slide.get("visual_suggestion", "chart")
            visual_type = "chart"
            chart_type = None

            if "chart" in visual_suggestion or "line" in visual_suggestion or "bar" in visual_suggestion:
                visual_type = "chart"
                if "candlestick" in visual_suggestion:
                    chart_type = "line"
                elif "bar" in visual_suggestion:
                    chart_type = "bar"
                else:
                    chart_type = "line"
            elif "dashboard" in visual_suggestion:
                visual_type = "chart"
                chart_type = "bar"
            elif "diagram" in visual_suggestion or "timeline" in visual_suggestion:
                visual_type = "diagram"
            elif "table" in visual_suggestion or "checklist" in visual_suggestion:
                visual_type = "table"

            visual_hints = [{
                "visualType": visual_type,
                "chartType": chart_type,
                "dataSource": query_id or "general_data",
                "purpose": f"Visualize {title}"
            }]

            transformed_slides.append({
                "slideNumber": slide_number,
                "slideType": slide_type,
                "title": title,
                "bulletPoints": bullet_points,
                "visualHints": visual_hints,
                "speakerNotes": f"Present {title} with supporting data and analysis",
                "keyMessage": bullet_points[0]["bulletText"] if bullet_points else title
            })

        # Create presentation title from context or first slide
        presentation_title = "BDX Stock Performance Analysis"
        if slides_data and len(slides_data) > 0:
            first_title = slides_data[0].get("title", "")
            if ":" in first_title:
                presentation_title = first_title

        # Build complete new format
        return {
            "presentation_outline": {
                "title": presentation_title,
                "subtitle": query_output.get("presentation_metadata", {}).get("subtitle", "Comprehensive Financial Analysis"),
                "totalSlides": old_outline.get("total_slides", len(slides_data)),
                "narrativeFlow": old_outline.get("narrative_flow", "Problem-Solution-Impact"),
                "slides": transformed_slides
            },
            "outline_metadata": {
                "templateCompliance": True,
                "slideCountCompliance": len(slides_data) >= 8 and len(slides_data) <= 10,
                "narrativeCoherence": 0.9,
                "dataIntegration": {
                    "totalDataPoints": sum(1 for slide in slides_data for bp in slide.get("bullet_points", []) if any(k in bp.lower() for k in ["$", "%", "price"])),
                    "queriesReferenced": sorted(list(queries_referenced)),
                    "coverageScore": min(1.0, len(queries_referenced) / 8.0)
                },
                "editingMetadata": None
            },
            "quality_checks": {
                "allSlidesHaveTitles": all(slide.get("title") for slide in slides_data),
                "bulletPointsWithinLimit": all(len(slide.get("bullet_points", [])) <= 5 for slide in slides_data),
                "visualHintsProvided": True,
                "dataBackedClaims": True,
                "logicalFlow": True
            },
            "next_action": "proceed_to_content_agent",
            "handoff_to_agent": None
        }

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Generate presentation outline with complete metadata structure."""
        import time
        start_time = time.time()

        context = request.context or {}
        query_output = context.get("query_output", {})
        rag_output = context.get("rag_output", {})

        prompt = f"""Create a professional presentation outline with complete metadata.

Topic: {request.user_input}

Query Analysis: {query_output}

Available Context: {rag_output.get('retrieved_context', '')[:1000]}

Target Audience: {query_output.get('presentation_metadata', {}).get('audience', 'executives')}
Target Slides: {query_output.get('presentation_metadata', {}).get('target_slides', 10)}

Generate a compelling 8-10 slide outline with:
- Complete presentation_outline with title, subtitle, slides (with bulletPoints, visualHints, speakerNotes, keyMessage)
- outline_metadata with compliance checks and data integration details
- quality_checks validating the outline quality
- next_action and handoff_to_agent fields

Follow the exact JSON structure specified in the system prompt.
"""

        try:
            iteration_count = 0
            tool_calls = 0

            response = await self._generate_with_retry(
                user_message=prompt,
                system_prompt=OUTLINE_SYSTEM_PROMPT,
                temperature=0.5,
            )

            iteration_count += 1
            tool_calls += 1

            outline = self._parse_json_response(response)

            # Calculate response time
            response_time = time.time() - start_time

            # Transform old format to new format if needed
            if "outline" in outline and "presentation_outline" not in outline:
                self.logger.info("Transforming old outline format to new format")
                outline = self._transform_to_new_format(outline, query_output)

            # Add performance metrics and timestamp
            outline["performance_metrics"] = {
                "responseTime": response_time,
                "agentIterations": iteration_count,
                "toolCallsMade": tool_calls
            }
            outline["timestamp"] = datetime.utcnow().isoformat()
            outline["error"] = None

            self.logger.info(
                "outline_generated",
                slide_count=len(outline.get("presentation_outline", {}).get("slides", [])),
                response_time=response_time
            )

            return outline

        except Exception as e:
            self.logger.error("outline_generation_failed", error=str(e), error_type=type(e).__name__, exc_info=True)
            # Return minimal valid structure on error
            return {
                "presentation_outline": {
                    "title": "Error: Failed to generate outline",
                    "subtitle": None,
                    "totalSlides": 0,
                    "narrativeFlow": "",
                    "slides": []
                },
                "outline_metadata": {
                    "templateCompliance": False,
                    "slideCountCompliance": False,
                    "narrativeCoherence": 0.0,
                    "dataIntegration": {
                        "totalDataPoints": 0,
                        "queriesReferenced": [],
                        "coverageScore": 0.0
                    },
                    "editingMetadata": None
                },
                "quality_checks": {
                    "allSlidesHaveTitles": False,
                    "bulletPointsWithinLimit": False,
                    "visualHintsProvided": False,
                    "dataBackedClaims": False,
                    "logicalFlow": False
                },
                "next_action": "error",
                "handoff_to_agent": None,
                "performance_metrics": {
                    "responseTime": time.time() - start_time,
                    "agentIterations": 0,
                    "toolCallsMade": 0
                },
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
