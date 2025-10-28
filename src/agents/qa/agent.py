"""QA Agent - Validate content against source documents using Claude-4."""
from typing import Any, Dict, List
import structlog

from src.agents.base import BaseAgent, AgentRequest, AgentType
from src.agents.config import get_agent_config

logger = structlog.get_logger(__name__)


QA_SYSTEM_PROMPT = """You are a meticulous quality assurance specialist for financial content.

Validate generated content against source documents:
1. Check factual accuracy of all numbers and metrics
2. Verify claims are supported by source data
3. Identify any hallucinations or unsupported statements
4. Check for consistency across slides
5. Flag any potential errors

Return JSON with validation results.
"""


class QAAgent(BaseAgent):
    """QA Agent using Claude-4 with ReAct + Self-Ask Pattern."""

    def __init__(self):
        config = get_agent_config(AgentType.QA)
        super().__init__(
            agent_name="qa_agent",
            agent_type=AgentType.QA,
            config=config,
        )

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Validate content accuracy."""
        context = request.context or {}
        content_output = context.get("content_output", {})
        rag_output = context.get("rag_output", {})

        prompt = f"""Validate this presentation content against source data:

Generated Content: {content_output}

Source Context: {rag_output.get('retrieved_context', '')[:3000]}
Source Documents: {rag_output.get('sources', [])}

Perform thorough validation and return:
{{
    "validation_passed": true/false,
    "accuracy_score": 0.95,
    "errors_found": [],
    "warnings": [],
    "recommendations": []
}}
"""

        try:
            response = await self._generate_with_retry(
                user_message=prompt,
                system_prompt=QA_SYSTEM_PROMPT,
                temperature=0.2,
            )

            validation = self._parse_json_response(response)

            self.logger.info(
                "qa_validation_complete",
                passed=validation.get("validation_passed"),
                accuracy=validation.get("accuracy_score"),
                errors=len(validation.get("errors_found", []))
            )

            return validation

        except Exception as e:
            self.logger.error("qa_validation_failed", error=str(e))
            return {
                "validation_passed": False,
                "accuracy_score": 0.0,
                "errors_found": [str(e)],
                "warnings": [],
                "recommendations": []
            }
