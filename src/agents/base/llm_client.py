"""LLM client factory and base classes for multi-provider support."""
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import structlog

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from cohere import AsyncClient as AsyncCohere

from .models import LLMProvider

logger = structlog.get_logger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        self.logger = logger.bind(
            llm_client=self.__class__.__name__,
            model=model_name
        )

    @abstractmethod
    async def generate(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    async def generate_with_tools(
        self,
        user_message: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response with tool calling support."""
        pass


class ClaudeClient(LLMClient):
    """Client for Anthropic Claude models."""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514", **kwargs):
        super().__init__(model_name, **kwargs)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate response using Claude."""
        messages = []

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": user_message})

        try:
            # Merge kwargs with defaults
            call_kwargs = {
                "model": self.model_name,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": messages,
            }

            if system_prompt:
                call_kwargs["system"] = system_prompt

            self.logger.debug("claude_api_call", **call_kwargs)

            response = await self.client.messages.create(**call_kwargs)

            # Extract text from response
            content = response.content[0].text if response.content else ""

            self.logger.info(
                "claude_api_success",
                tokens_used=response.usage.total_tokens,
                response_length=len(content)
            )

            return content

        except Exception as e:
            self.logger.error("claude_api_error", error=str(e), error_type=type(e).__name__)
            raise

    async def generate_with_tools(
        self,
        user_message: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response with tool calling."""
        messages = [{"role": "user", "content": user_message}]

        try:
            call_kwargs = {
                "model": self.model_name,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": messages,
                "tools": tools,
            }

            if system_prompt:
                call_kwargs["system"] = system_prompt

            response = await self.client.messages.create(**call_kwargs)

            return {
                "content": response.content[0].text if response.content else "",
                "tool_calls": getattr(response, "tool_calls", []),
                "stop_reason": response.stop_reason,
            }

        except Exception as e:
            self.logger.error("claude_tool_call_error", error=str(e))
            raise


class GPTClient(LLMClient):
    """Client for OpenAI GPT models."""

    def __init__(self, model_name: str = "gpt-4-turbo", **kwargs):
        super().__init__(model_name, **kwargs)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate response using GPT."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            content = response.choices[0].message.content

            self.logger.info(
                "gpt_api_success",
                tokens_used=response.usage.total_tokens,
                response_length=len(content)
            )

            return content

        except Exception as e:
            self.logger.error("gpt_api_error", error=str(e))
            raise

    async def generate_with_tools(
        self,
        user_message: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response with tool calling."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            message = response.choices[0].message

            return {
                "content": message.content or "",
                "tool_calls": message.tool_calls if hasattr(message, "tool_calls") else [],
                "finish_reason": response.choices[0].finish_reason,
            }

        except Exception as e:
            self.logger.error("gpt_tool_call_error", error=str(e))
            raise


class CohereClient(LLMClient):
    """Client for Cohere models."""

    def __init__(self, model_name: str = "command-r-plus", **kwargs):
        super().__init__(model_name, **kwargs)
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")
        self.client = AsyncCohere(api_key=api_key)

    async def generate(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate response using Cohere."""
        # Build the message with system prompt prepended
        message = user_message
        if system_prompt:
            message = f"{system_prompt}\n\n{user_message}"

        try:
            # Convert conversation history to Cohere format if provided
            chat_history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "USER" if msg["role"] == "user" else "CHATBOT"
                    chat_history.append({"role": role, "message": msg["content"]})

            response = await self.client.chat(
                model=self.model_name,
                message=message,
                chat_history=chat_history if chat_history else None,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            content = response.text

            self.logger.info(
                "cohere_api_success",
                response_length=len(content)
            )

            return content

        except Exception as e:
            self.logger.error("cohere_api_error", error=str(e))
            raise

    async def generate_with_tools(
        self,
        user_message: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response with tool calling."""
        message = user_message
        if system_prompt:
            message = f"{system_prompt}\n\n{user_message}"

        try:
            response = await self.client.chat(
                model=self.model_name,
                message=message,
                tools=tools,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            return {
                "content": response.text,
                "tool_calls": getattr(response, "tool_calls", []),
            }

        except Exception as e:
            self.logger.error("cohere_tool_call_error", error=str(e))
            raise


class LLMClientFactory:
    """Factory for creating LLM clients."""

    @staticmethod
    def create_client(
        provider: LLMProvider,
        model_name: Optional[str] = None,
        **kwargs
    ) -> LLMClient:
        """Create an LLM client based on provider.

        Args:
            provider: LLM provider enum
            model_name: Optional specific model name
            **kwargs: Additional arguments for the client

        Returns:
            Configured LLM client instance
        """
        if provider == LLMProvider.ANTHROPIC:
            model = model_name or "claude-sonnet-4-20250514"
            return ClaudeClient(model_name=model, **kwargs)

        elif provider == LLMProvider.OPENAI:
            model = model_name or "gpt-4-turbo"
            return GPTClient(model_name=model, **kwargs)

        elif provider == LLMProvider.COHERE:
            model = model_name or "command-r-plus"
            return CohereClient(model_name=model, **kwargs)

        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: ANTHROPIC, OPENAI, COHERE")
