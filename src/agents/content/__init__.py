"""
Content Agent Module
Expands presentation outlines into comprehensive content
"""

from .agent import ContentAgent

from .models import (
    ContentAgentInput,
    ContentAgentOutput,
    ExtractedInformation,
    DataRequirements,
    PresentationRequirements,
    VisualPreferences,
    OutlineAgentOutput,
    PresentationOutline,
    RAGQueryRequest,
    RAGQueryResponse,
    ExpandedPresentationContent,
    ExpandedSlideContent,
    ExpandedBulletPoint,
    VisualElement,
    ContentDataMapping,
    ContentMetadata,
    ContentQualityChecks,
    PerformanceMetrics
)

from .prompts import (
    CONTENT_AGENT_SYSTEM_PROMPT,
    get_rag_query_prompt,
    get_content_expansion_prompt,
    get_visual_specification_prompt,
    get_speaker_notes_prompt
)

__all__ = [
    # Agent
    "ContentAgent",

    # Input Models
    "ContentAgentInput",
    "ContentAgentOutput",
    "ExtractedInformation",
    "DataRequirements",
    "PresentationRequirements",
    "VisualPreferences",
    "OutlineAgentOutput",
    "PresentationOutline",

    # Output Models
    "ExpandedPresentationContent",
    "ExpandedSlideContent",
    "ExpandedBulletPoint",
    "VisualElement",
    "ContentDataMapping",
    "ContentMetadata",
    "ContentQualityChecks",
    "PerformanceMetrics",

    # RAG Models
    "RAGQueryRequest",
    "RAGQueryResponse",

    # Prompts
    "CONTENT_AGENT_SYSTEM_PROMPT",
    "get_rag_query_prompt",
    "get_content_expansion_prompt",
    "get_visual_specification_prompt",
    "get_speaker_notes_prompt",
]

__version__ = "1.0.0"
__author__ = "ConvoSynth Team"
__description__ = "Content Agent for expanding presentation outlines into detailed content"