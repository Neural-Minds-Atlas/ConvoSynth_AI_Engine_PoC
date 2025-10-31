"""Outline Agent module for presentation outline generation and editing."""

from .agent import OutlineAgent, create_outline_agent
from .prompts import (
    OUTLINE_AGENT_SYSTEM_PROMPT,
    OUTLINE_GENERATION_PROMPT,
    OUTLINE_EDITING_PROMPT,
    REACT_AGENT_TEMPLATE
)

__all__ = [
    "OutlineAgent",
    "create_outline_agent",
    "OUTLINE_AGENT_SYSTEM_PROMPT",
    "OUTLINE_GENERATION_PROMPT",
    "OUTLINE_EDITING_PROMPT",
    "REACT_AGENT_TEMPLATE"
]