"""Image Coordination Agent - Generate images and visualizations using GPT-4."""
from typing import Any, Dict, List
import structlog

from src.agents.base import BaseAgent, AgentRequest, AgentType
from src.agents.config import get_agent_config

logger = structlog.get_logger(__name__)


IMAGE_SYSTEM_PROMPT = """You are a visualization expert for financial presentations.

For each slide, determine:
1. Whether an image/chart is needed
2. Type of visualization (bar chart, line chart, pie chart, infographic, icon)
3. Specific data to visualize
4. Design specifications

Return JSON with visualization instructions for each slide.
"""


class ImageCoordinationAgent(BaseAgent):
    """Image Coordination Agent using GPT-4/5 with Tool Calling."""

    def __init__(self):
        config = get_agent_config(AgentType.IMAGE_COORDINATION)
        super().__init__(
            agent_name="image_coordination_agent",
            agent_type=AgentType.IMAGE_COORDINATION,
            config=config,
        )

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Generate visualization specifications."""
        context = request.context or {}
        content_output = context.get("content_output", {})
        slides = content_output.get("slides", [])

        visualizations = []

        for slide in slides:
            viz_spec = await self._generate_visualization_spec(slide)
            visualizations.append(viz_spec)

        return {
            "visualizations": visualizations,
            "total_visuals": len(visualizations)
        }

    async def _generate_visualization_spec(self, slide: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization specification for a slide."""
        prompt = f"""Determine visualization for this slide:

Slide {slide.get('slide_number')}: {slide.get('title')}
Content: {slide.get('content', {})}

What type of visualization would best represent this data?

Return JSON:
{{
    "slide_number": {slide.get('slide_number')},
    "requires_visual": true,
    "visual_type": "bar_chart/line_chart/pie_chart/icon/image",
    "data_to_visualize": {{}},
    "chart_config": {{
        "title": "Chart Title",
        "x_axis": "label",
        "y_axis": "label",
        "colors": ["#color1", "#color2"]
    }},
    "alt_text": "Description for accessibility"
}}
"""

        try:
            response = await self._generate_with_retry(
                user_message=prompt,
                system_prompt=IMAGE_SYSTEM_PROMPT,
                temperature=0.7,
            )

            viz_spec = self._parse_json_response(response)
            return viz_spec

        except Exception as e:
            self.logger.error("visualization_spec_failed", error=str(e), slide=slide.get('slide_number'))
            return {
                "slide_number": slide.get('slide_number'),
                "requires_visual": False
            }
