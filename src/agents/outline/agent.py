"""Outline Agent - Generate presentation structure using Claude-4/GPT-4."""
from typing import Any, Dict
import structlog

from src.agents.base import BaseAgent, AgentRequest, AgentType
from src.agents.config import get_agent_config

logger = structlog.get_logger(__name__)


OUTLINE_SYSTEM_PROMPT = """You are an expert presentation architect specializing in financial presentations.

Generate an 8-10 slide structured outline with:
- Clear slide titles
- 3-5 key bullet points per slide
- Logical flow and narrative arc
- Professional business structure

Return JSON:
{
    "outline": [
        {
            "slide_number": 1,
            "title": "Executive Summary",
            "bullet_points": [
                "Key financial highlights",
                "Major achievements",
                "Strategic direction"
            ],
            "estimated_content_length": "medium",
            "visual_suggestion": "chart"
        }
    ],
    "narrative_flow": "Problem-Solution-Impact structure",
    "total_slides": 10
}
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

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Generate presentation outline."""
        context = request.context or {}
        query_output = context.get("query_output", {})
        rag_output = context.get("rag_output", {})

        prompt = f"""Create a professional presentation outline.

Topic: {request.user_input}

Query Analysis: {query_output}

Available Context: {rag_output.get('retrieved_context', '')[:1000]}

Target Audience: {query_output.get('presentation_metadata', {}).get('audience', 'executives')}
Target Slides: {query_output.get('presentation_metadata', {}).get('target_slides', 10)}

Generate a compelling 8-10 slide outline.
"""

        try:
            response = await self._generate_with_retry(
                user_message=prompt,
                system_prompt=OUTLINE_SYSTEM_PROMPT,
                temperature=0.5,
            )

            outline = self._parse_json_response(response)

            self.logger.info(
                "outline_generated",
                slide_count=len(outline.get("outline", []))
            )

            return outline

        except Exception as e:
            self.logger.error("outline_generation_failed", error=str(e))
            return {"outline": [], "narrative_flow": "linear", "total_slides": 0}
