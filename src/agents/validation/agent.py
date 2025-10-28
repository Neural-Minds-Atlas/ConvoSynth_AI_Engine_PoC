"""Validation Engine - Final completeness check using Claude-4."""
from typing import Any, Dict, List
import structlog

from src.agents.base import BaseAgent, AgentRequest, AgentType
from src.agents.config import get_agent_config

logger = structlog.get_logger(__name__)


VALIDATION_SYSTEM_PROMPT = """You are a systematic validation engine for presentations.

Validate presentation completeness:
1. All required slides present
2. All user preferences implemented
3. All requested information included
4. Proper formatting applied
5. Visualizations correctly placed
6. No missing content
7. Consistent style throughout

Return JSON with comprehensive validation results.
"""


class ValidationAgent(BaseAgent):
    """Validation Engine using Claude-4 with Plan-and-Execute."""

    def __init__(self):
        config = get_agent_config(AgentType.VALIDATION)
        super().__init__(
            agent_name="validation_engine",
            agent_type=AgentType.VALIDATION,
            config=config,
        )

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Validate final presentation completeness."""
        context = request.context or {}
        original_request = request.user_input
        preferences = request.preferences or {}

        # Gather all outputs
        outline_output = context.get("outline_output", {})
        content_output = context.get("content_output", {})
        image_output = context.get("image_output", {})
        format_output = context.get("format_output", {})
        qa_output = context.get("qa_output", {})

        prompt = f"""Perform final validation of this presentation:

Original Request: {original_request}
User Preferences: {preferences}

Outline: {outline_output.get('total_slides')} slides planned
Content: {content_output.get('total_slides')} slides with content
Images: {image_output.get('total_visuals')} visualizations
Format: {format_output.get('format')} - Valid: {format_output.get('is_valid')}
QA Results: Passed: {qa_output.get('validation_passed')}, Accuracy: {qa_output.get('accuracy_score')}

Check completeness and return:
{{
    "validation_passed": true/false,
    "completeness_score": 1.0,
    "checklist": {{
        "all_slides_present": true,
        "preferences_applied": true,
        "content_complete": true,
        "formatting_correct": true,
        "visualizations_included": true
    }},
    "issues": [],
    "missing_items": [],
    "recommendations": [],
    "ready_for_delivery": true
}}
"""

        try:
            response = await self._generate_with_retry(
                user_message=prompt,
                system_prompt=VALIDATION_SYSTEM_PROMPT,
                temperature=0.1,
            )

            validation = self._parse_json_response(response)

            self.logger.info(
                "validation_complete",
                passed=validation.get("validation_passed"),
                completeness=validation.get("completeness_score"),
                ready=validation.get("ready_for_delivery")
            )

            return validation

        except Exception as e:
            self.logger.error("validation_failed", error=str(e))
            return {
                "validation_passed": False,
                "completeness_score": 0.0,
                "checklist": {},
                "issues": [str(e)],
                "missing_items": [],
                "recommendations": [],
                "ready_for_delivery": False
            }
