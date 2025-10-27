"""Base agent class for all agents in the system."""
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import structlog

from .models import (
    AgentRequest,
    AgentResponse,
    AgentType,
    AgentConfig,
    LLMProvider,
)
from .llm_client import LLMClientFactory, LLMClient

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents.

    All agents should inherit from this class and implement the _execute method.
    """

    def __init__(
        self,
        agent_name: str,
        agent_type: Optional[AgentType] = None,
        config: Optional[AgentConfig] = None,
    ):
        """Initialize the base agent.

        Args:
            agent_name: Name identifier for the agent
            agent_type: Type of the agent
            config: Agent configuration
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.config = config
        self.logger = logger.bind(agent=agent_name)

        # Initialize LLM client if config provided
        self.llm_client: Optional[LLMClient] = None
        if config:
            self.llm_client = LLMClientFactory.create_client(
                provider=config.llm_provider,
                model_name=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )

        self.logger.info(
            "agent_initialized",
            agent_type=str(agent_type) if agent_type else None,
            has_llm_client=self.llm_client is not None,
        )

    @abstractmethod
    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute the agent's core logic.

        This method must be implemented by all subclasses.

        Args:
            request: Agent request with input data

        Returns:
            Dictionary containing the agent's output
        """
        pass

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the agent with error handling and metrics.

        Args:
            request: Agent request

        Returns:
            Agent response with output and metadata
        """
        start_time = time.time()
        errors = []

        self.logger.info(
            "agent_execution_started",
            user_input_length=len(request.user_input),
            has_context=bool(request.context),
            has_documents=bool(request.documents),
        )

        try:
            # Execute the agent's core logic
            output = await self._execute(request)

            # Calculate execution time
            execution_time = time.time() - start_time

            self.logger.info(
                "agent_execution_completed",
                execution_time=execution_time,
                output_keys=list(output.keys()) if isinstance(output, dict) else None,
            )

            # Check if execution time meets target
            if self.config and self.config.response_time_target:
                if execution_time > self.config.response_time_target:
                    self.logger.warning(
                        "response_time_exceeded",
                        actual=execution_time,
                        target=self.config.response_time_target,
                    )

            return AgentResponse(
                agent_type=self.agent_type or AgentType.CONVERSATION,
                success=True,
                output=output,
                metadata={
                    "agent_name": self.agent_name,
                    "execution_time": execution_time,
                    "model": self.config.model_name if self.config else None,
                    "timestamp": time.time(),
                },
                errors=None,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            errors.append(error_msg)

            self.logger.error(
                "agent_execution_failed",
                error=error_msg,
                execution_time=execution_time,
            )

            return AgentResponse(
                agent_type=self.agent_type or AgentType.CONVERSATION,
                success=False,
                output={},
                metadata={
                    "agent_name": self.agent_name,
                    "execution_time": execution_time,
                    "error_type": type(e).__name__,
                    "timestamp": time.time(),
                },
                errors=errors,
            )

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response.

        Handles responses with or without markdown code blocks.

        Args:
            response: Raw response from LLM

        Returns:
            Parsed JSON dictionary
        """
        import json

        response = response.strip()

        # Try to extract JSON from markdown code blocks
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            self.logger.error("json_parse_error", error=str(e), response=response[:200])
            raise ValueError(f"Failed to parse JSON response: {str(e)}")

    async def _generate_with_retry(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate LLM response with retry logic.

        Args:
            user_message: User message
            system_prompt: System prompt
            max_retries: Maximum number of retries (uses config if not provided)
            **kwargs: Additional arguments for LLM client

        Returns:
            Generated response

        Raises:
            Exception: If all retries fail
        """
        if not self.llm_client:
            raise ValueError("LLM client not initialized")

        retries = max_retries if max_retries is not None else (
            self.config.max_retries if self.config else 3
        )

        last_error = None

        for attempt in range(retries + 1):
            try:
                response = await self.llm_client.generate(
                    user_message=user_message,
                    system_prompt=system_prompt,
                    **kwargs
                )
                return response

            except Exception as e:
                last_error = e
                self.logger.warning(
                    "llm_generation_retry",
                    attempt=attempt + 1,
                    max_retries=retries,
                    error=str(e),
                )

                if attempt < retries:
                    # Exponential backoff
                    await self._async_sleep(2 ** attempt)
                else:
                    break

        self.logger.error("llm_generation_failed", error=str(last_error))
        raise last_error

    @staticmethod
    async def _async_sleep(seconds: float):
        """Async sleep helper."""
        import asyncio
        await asyncio.sleep(seconds)
