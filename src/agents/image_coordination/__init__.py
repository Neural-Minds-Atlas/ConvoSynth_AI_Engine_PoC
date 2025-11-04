"""
Image Coordination Agent Module

Converts visual element specifications into Chart.js compatible configurations.
Supports bar charts, line charts, pie charts, and area charts.
"""

from .agent import (
    # Agent
    ImageCoordinationAgent,
    create_image_coordination_agent,
    
    # Input Models
    ImageCoordinationInput,
    VisualElement,
    DataPoint,
    
    # Output Models
    ImageCoordinationOutput,
    ChartOutput,
    ChartJSConfig,
    ChartJSData,
    ChartJSDataset,
    ChartJSOptions,
    ChartJSTextProperties,
    ChartJSPlugins,
    
    # Tools
    generate_chart_config_tool,
    
    # Helper Functions
    parse_color_scheme,
    map_chart_type
)

from .prompts import (
    get_react_prompt_template,
    get_direct_generation_prompt,
    get_validation_prompt,
    REACT_AGENT_TEMPLATE,
    SYSTEM_PROMPT,
    HUMAN_PROMPT,
    DIRECT_GENERATION_PROMPT,
    VALIDATION_PROMPT
)


__all__ = [
    # Agent
    "ImageCoordinationAgent",
    "create_image_coordination_agent",
    
    # Input Models
    "ImageCoordinationInput",
    "VisualElement",
    "DataPoint",
    
    # Output Models
    "ImageCoordinationOutput",
    "ChartOutput",
    "ChartJSConfig",
    "ChartJSData",
    "ChartJSDataset",
    "ChartJSOptions",
    "ChartJSTextProperties",
    "ChartJSPlugins",
    
    # Tools
    "generate_chart_config_tool",
    
    # Helper Functions
    "parse_color_scheme",
    "map_chart_type",
    
    # Prompts
    "get_react_prompt_template",
    "get_direct_generation_prompt",
    "get_validation_prompt",
    "REACT_AGENT_TEMPLATE",
    "SYSTEM_PROMPT",
    "HUMAN_PROMPT",
    "DIRECT_GENERATION_PROMPT",
    "VALIDATION_PROMPT"
]


# Version
__version__ = "1.0.0"

# Agent metadata
__agent_name__ = "Image Coordination Agent"
__agent_function__ = "Generate Chart.js configurations from visual specifications"
__llm_model__ = "claude-sonnet-4-20250514"
__response_time_target__ = "<2s"
__accuracy_target__ = "90% visual relevance"