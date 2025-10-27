"""LLM service for interacting with Claude API."""
from typing import Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import AgentException

logger = get_logger(__name__)


class LLMService:
    """Service for LLM interactions."""

    def __init__(self):
        """Initialize LLM service with Anthropic Claude."""
        self.llm = ChatAnthropic(
            model=settings.anthropic_model,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=settings.anthropic_temperature,
            max_tokens=settings.anthropic_max_tokens,
            timeout=settings.anthropic_timeout,
        )

        logger.info(
            "llm_service_initialized",
            model=settings.anthropic_model,
            temperature=settings.anthropic_temperature,
            max_tokens=settings.anthropic_max_tokens,
        )

    async def generate_response(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated text response

        Raises:
            AgentException: If generation fails
        """
        try:
            messages = []

            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))

            messages.append(HumanMessage(content=prompt))

            response = await self.llm.ainvoke(messages)

            logger.info(
                "llm_response_generated",
                prompt_length=len(prompt),
                response_length=len(response.content)
            )

            return response.content

        except Exception as e:
            logger.error("llm_generation_failed", error=str(e), prompt_preview=prompt[:100])
            raise AgentException(
                message="Failed to generate LLM response",
                details={"error": str(e)}
            )

    def invoke_sync(self, prompt: str) -> str:
        """Synchronously invoke the LLM (for tool use).

        Args:
            prompt: Prompt to send

        Returns:
            Generated response
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error("llm_sync_invoke_failed", error=str(e))
            return f"Error: {str(e)}"

    async def ainvoke(self, messages: list) -> Any:
        """Async invoke with message list.

        Args:
            messages: List of messages

        Returns:
            LLM response
        """
        return await self.llm.ainvoke(messages)

    def get_llm_instance(self) -> ChatAnthropic:
        """Get the underlying LLM instance.

        Returns:
            ChatAnthropic instance
        """
        return self.llm
