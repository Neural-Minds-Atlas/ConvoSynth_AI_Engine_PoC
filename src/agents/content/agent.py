"""Content Agent - Expand outline into full slide content using Claude-4."""
from typing import Any, Dict, List
import structlog

from src.agents.base import BaseAgent, AgentRequest, AgentType
from src.agents.config import get_agent_config

logger = structlog.get_logger(__name__)


CONTENT_SYSTEM_PROMPT = """You are a financial content writer with expertise in creating compelling presentation content.

Expand outline bullet points into clear, concise slide content:
- Use data from retrieved context
- Include specific metrics and numbers
- Maintain professional tone
- Be accurate with financial data
- Keep content slide-appropriate (not too dense)

Return JSON with expanded content for each slide.
"""


class ContentAgent(BaseAgent):
    """Content Agent using Claude-4 with Zero-shot ReAct."""

    def __init__(self):
        config = get_agent_config(AgentType.CONTENT)
        super().__init__(
            agent_name="content_agent",
            agent_type=AgentType.CONTENT,
            config=config,
        )

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Expand outline into full content."""
        context = request.context or {}
        outline = context.get("outline_output", {}).get("outline", [])
        rag_output = context.get("rag_output", {})

        slides_content = []

        for slide_info in outline:
            content = await self._generate_slide_content(slide_info, rag_output)
            slides_content.append(content)

        return {
            "slides": slides_content,
            "total_slides": len(slides_content)
        }

    async def _generate_slide_content(
        self,
        slide_info: Dict[str, Any],
        rag_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content for a single slide."""
        prompt = f"""Expand this slide outline into full content:

Slide {slide_info.get('slide_number')}: {slide_info.get('title')}
Bullet Points: {slide_info.get('bullet_points', [])}

Available Context: {rag_output.get('retrieved_context', '')[:2000]}
Key Findings: {rag_output.get('key_findings', [])}

Generate detailed, accurate content with specific data points.

Return JSON:
{{
    "slide_number": {slide_info.get('slide_number')},
    "title": "{slide_info.get('title')}",
    "content": {{
        "main_points": ["point 1 with data", "point 2 with data"],
        "supporting_data": {{"metric": "value"}},
        "narrative": "connecting text"
    }}
}}
"""

        try:
            response = await self._generate_with_retry(
                user_message=prompt,
                system_prompt=CONTENT_SYSTEM_PROMPT,
                temperature=0.6,
            )

            content = self._parse_json_response(response)
            return content

        except Exception as e:
            self.logger.error("content_generation_failed", error=str(e), slide=slide_info.get('slide_number'))
            return {"slide_number": slide_info.get('slide_number'), "title": slide_info.get('title'), "content": {}}
