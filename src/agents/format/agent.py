"""Format Agent - Generate professional HTML using Claude-4."""
from typing import Any, Dict
import structlog

from src.agents.base import BaseAgent, AgentRequest, AgentType
from src.agents.config import get_agent_config

logger = structlog.get_logger(__name__)


FORMAT_SYSTEM_PROMPT = """You are an expert HTML/CSS developer specializing in presentation formatting.

Generate professional, responsive HTML for presentations:
- Use modern CSS (Flexbox/Grid)
- Ensure mobile responsiveness
- Apply professional styling
- Integrate visualizations
- Follow accessibility standards
- Use semantic HTML

Return complete, valid HTML document.
"""


class FormatAgent(BaseAgent):
    """Format Agent using Claude-4 with Zero-shot Structured Output."""

    def __init__(self):
        config = get_agent_config(AgentType.FORMAT)
        super().__init__(
            agent_name="format_agent",
            agent_type=AgentType.FORMAT,
            config=config,
        )

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Generate HTML presentation."""
        context = request.context or {}
        content_output = context.get("content_output", {})
        image_output = context.get("image_output", {})
        preferences = request.preferences or {}

        prompt = f"""Generate a professional HTML presentation.

Slides Content: {content_output}

Visualizations: {image_output}

User Preferences:
- Theme: {preferences.get('theme', 'professional')}
- Color Scheme: {preferences.get('color_scheme', 'blue')}
- Font: {preferences.get('font', 'Arial')}

Generate complete HTML with:
1. <!DOCTYPE html> declaration
2. Responsive CSS
3. Professional styling
4. Slide navigation
5. Print-friendly styles

Return the full HTML document as a string.
"""

        try:
            response = await self._generate_with_retry(
                user_message=prompt,
                system_prompt=FORMAT_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=8192,
            )

            # Extract HTML if wrapped in code blocks
            html_content = response
            if "```html" in response:
                html_content = response.split("```html")[1].split("```")[0].strip()
            elif "```" in response:
                html_content = response.split("```")[1].split("```")[0].strip()

            self.logger.info(
                "html_generated",
                length=len(html_content)
            )

            return {
                "html": html_content,
                "format": "html",
                "is_valid": "<!DOCTYPE" in html_content or "<html" in html_content
            }

        except Exception as e:
            self.logger.error("format_generation_failed", error=str(e))
            return {
                "html": "<html><body><h1>Error generating presentation</h1></body></html>",
                "format": "html",
                "is_valid": False,
                "error": str(e)
            }
