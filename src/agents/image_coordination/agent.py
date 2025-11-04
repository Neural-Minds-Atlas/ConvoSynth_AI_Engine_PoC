"""
Image Coordination Agent - Chart.js Configuration Generator
Converts visual element specifications into Chart.js compatible configurations
"""

import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
import json
import re


# ==================== INPUT MODELS ====================

class DataPoint(BaseModel):
    """Data point for chart visualization"""
    x: str = Field(..., description="X-axis value/label")
    y: float = Field(..., description="Y-axis numeric value")
    label: str = Field(..., description="Data point label")
    category: Optional[str] = Field(None, description="Category for grouping")
    volume: Optional[float] = Field(None, description="Secondary metric (e.g., volume)")


class VisualElement(BaseModel):
    """Visual element specification for chart generation"""
    visualType: str = Field(..., description="Type of visual: 'chart', 'image', etc.")
    chartType: str = Field(..., description="Chart type: 'bar_chart', 'line_chart', 'pie_chart', 'area_chart'")
    dataSource: str = Field(..., description="Source of the data")
    dataValue: str = Field(..., description="Description of data values")
    purpose: str = Field(..., description="Purpose of the visualization")
    xAxisLabel: str = Field(..., description="Label for X-axis")
    yAxisLabel: str = Field(..., description="Label for Y-axis")
    title: str = Field(..., description="Chart title")
    dataPoints: List[DataPoint] = Field(..., description="Array of data points to plot")
    colorScheme: str = Field(..., description="Color scheme description")
    annotations: List[str] = Field(default_factory=list, description="Additional annotations/notes")


class ImageCoordinationInput(BaseModel):
    """Input schema for Image Coordination Agent"""
    session_id: str = Field(..., description="Session identifier")
    id: str = Field(..., description="Unique request identifier")
    presentation_id: Optional[str] = Field(None, description="Presentation identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    visualElements: List[VisualElement] = Field(..., description="Array of visual elements to generate")


# ==================== OUTPUT MODELS ====================

class ChartJSDataset(BaseModel):
    """Chart.js dataset structure"""
    label: str
    data: List[float]
    backgroundColor: List[str]
    borderColor: Optional[List[str]] = None


class ChartJSData(BaseModel):
    """Chart.js data structure"""
    labels: List[str]
    datasets: List[ChartJSDataset]


class ChartJSTextProperties(BaseModel):
    """Chart.js text styling properties"""
    fontFamily: str = "Poppins"
    fontSize: int = 14
    color: str = "#000000"


class ChartJSPlugins(BaseModel):
    """Chart.js plugins configuration"""
    legend: Dict[str, bool] = {"display": False}
    tooltip: Dict[str, bool] = {"enabled": False}
    title: Dict[str, Any]


class ChartJSOptions(BaseModel):
    """Chart.js options configuration"""
    format: str = "number"
    title: str
    textProperties: ChartJSTextProperties
    responsive: bool = True
    maintainAspectRatio: bool = False
    animation: bool = False
    plugins: ChartJSPlugins


class ChartJSConfig(BaseModel):
    """Chart.js configuration structure"""
    type: str
    data: ChartJSData
    options: ChartJSOptions


class ChartOutput(BaseModel):
    """Complete chart output with ID and config"""
    id: str
    cfg: ChartJSConfig
    exportScale: float = 0.7


class ImageCoordinationOutput(BaseModel):
    """Output schema for Image Coordination Agent"""
    session_id: str
    id: str
    presentation_id: Optional[str]
    user_id: Optional[str]
    generatedCharts: List[ChartOutput]
    chartCount: int
    timestamp: str


# ==================== HELPER FUNCTIONS ====================

def parse_color_scheme(color_scheme: str) -> List[str]:
    """
    Parse color scheme description and extract hex colors.
    Returns default colors if parsing fails.
    """
    default_colors = ["#2376DD", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]
    
    # Extract hex colors from the description
    hex_pattern = r'#[0-9A-Fa-f]{6}'
    colors = re.findall(hex_pattern, color_scheme)
    
    if colors:
        return colors
    
    # Fallback to default colors
    return default_colors


def map_chart_type(chart_type: str) -> str:
    """
    Map internal chart type names to Chart.js types.
    
    bar_chart -> bar
    line_chart -> line
    pie_chart -> pie
    area_chart -> line (with fill enabled)
    """
    mapping = {
        "bar_chart": "bar",
        "line_chart": "line",
        "pie_chart": "pie",
        "area_chart": "line",  # Area charts are line charts with fill
        "bar": "bar",
        "line": "line",
        "pie": "pie",
        "area": "line"
    }
    return mapping.get(chart_type.lower(), "bar")


# ==================== TOOL: GENERATE CHART CONFIG ====================

def generate_chart_config_tool(
    visual_element: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Tool to generate Chart.js configuration from visual element specification.
    
    Args:
        visual_element: Dictionary containing visual element specification
        
    Returns:
        Chart.js configuration object
    """
    try:
        # Parse the visual element
        ve = VisualElement(**visual_element)
        
        # Generate unique chart ID
        chart_id = f"chart-{uuid.uuid4()}"
        
        # Map chart type
        chart_js_type = map_chart_type(ve.chartType)
        
        # Extract labels and data from dataPoints
        labels = [dp.x for dp in ve.dataPoints]
        data_values = [dp.y for dp in ve.dataPoints]
        
        # Parse color scheme
        colors = parse_color_scheme(ve.colorScheme)
        
        # Ensure we have enough colors for all data points
        while len(colors) < len(data_values):
            colors.extend(colors)
        
        # Truncate to match data length
        bg_colors = colors[:len(data_values)]
        border_colors = colors[:len(data_values)]
        
        # Build dataset
        dataset = {
            "label": "Series 1",
            "data": data_values,
            "backgroundColor": bg_colors
        }
        
        # Add borderColor for line charts
        if chart_js_type == "line":
            dataset["borderColor"] = border_colors
        
        # Build Chart.js config
        chart_config = {
            "id": chart_id,
            "cfg": {
                "type": chart_js_type,
                "data": {
                    "labels": labels,
                    "datasets": [dataset]
                },
                "options": {
                    "format": "number",
                    "title": ve.title,
                    "textProperties": {
                        "fontFamily": "Poppins",
                        "fontSize": 14,
                        "color": "#000000"
                    },
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "animation": False,
                    "plugins": {
                        "legend": {
                            "display": False
                        },
                        "tooltip": {
                            "enabled": False
                        },
                        "title": {
                            "display": True,
                            "text": ve.title
                        }
                    }
                }
            },
            "exportScale": 0.7
        }
        
        return {
            "success": True,
            "chart_config": chart_config,
            "chart_id": chart_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "chart_config": None
        }


# ==================== IMAGE COORDINATION AGENT ====================

class ImageCoordinationAgent:
    """
    Image Coordination Agent for generating Chart.js configurations.
    Uses Claude Sonnet 4 for intelligent visual specification parsing.
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        model_name: str = "claude-sonnet-4-20250514",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        verbose: bool = True
    ):
        """
        Initialize the Image Coordination Agent.
        
        Args:
            anthropic_api_key: Anthropic API key
            model_name: Claude model to use
            temperature: LLM temperature (lower for consistent formatting)
            max_tokens: Maximum tokens for response
            verbose: Enable verbose logging
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.verbose = verbose
        
        # Initialize Claude LLM
        self.llm = ChatAnthropic(
            model=model_name,
            anthropic_api_key=anthropic_api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
        
        # Create executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        return [
            Tool(
                name="generate_chart_config",
                func=lambda x: json.dumps(generate_chart_config_tool(json.loads(x) if isinstance(x, str) else x)),
                description=(
                    "Generate Chart.js configuration from visual element specification. "
                    "Input: JSON string of visual element object. "
                    "Returns: JSON string with chart configuration. "
                    "Use this tool for each visual element that needs to be converted to a chart."
                )
            )
        ]
    
    def _create_agent(self):
        """Create the ReAct agent"""
        from .prompts import get_react_prompt_template
        
        prompt = get_react_prompt_template()
        
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    def process(self, input_data: ImageCoordinationInput) -> ImageCoordinationOutput:
        """
        Process visual elements and generate Chart.js configurations.
        
        Args:
            input_data: ImageCoordinationInput with visual elements
            
        Returns:
            ImageCoordinationOutput with generated chart configs
        """
        try:
            # Prepare input for agent - only pass 'input', AgentExecutor handles the rest
            agent_input = {
                "input": json.dumps({
                    "session_id": input_data.session_id,
                    "id": input_data.id,
                    "presentation_id": input_data.presentation_id,
                    "user_id": input_data.user_id,
                    "visualElements": [ve.model_dump() for ve in input_data.visualElements],
                    "elementCount": len(input_data.visualElements)
                }, indent=2)
            }
            
            # Execute agent
            result = self.executor.invoke(agent_input)
            
            # Parse agent output
            output_text = result.get("output", "")
            
            # Extract chart configs from the output
            charts = self._extract_charts_from_output(output_text, input_data.visualElements)
            
            # Build output
            from datetime import datetime
            
            output = ImageCoordinationOutput(
                session_id=input_data.session_id,
                id=input_data.id,
                presentation_id=input_data.presentation_id,
                user_id=input_data.user_id,
                generatedCharts=charts,
                chartCount=len(charts),
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            
            return output
            
        except Exception as e:
            # Fallback: generate charts directly without agent reasoning
            print(f"Agent execution failed, using direct generation: {e}")
            return self._direct_generation_fallback(input_data)
    
    def _extract_charts_from_output(
        self,
        output_text: str,
        visual_elements: List[VisualElement]
    ) -> List[ChartOutput]:
        """
        Extract chart configurations from agent output text.
        Falls back to direct generation if parsing fails.
        """
        try:
            # Try to find JSON array in output
            json_match = re.search(r'\[[\s\S]*\]', output_text)
            if json_match:
                charts_data = json.loads(json_match.group())
                return [ChartOutput(**chart) for chart in charts_data]
        except:
            pass
        
        # Fallback: generate directly
        charts = []
        for ve in visual_elements:
            result = generate_chart_config_tool(ve.model_dump())
            if result["success"]:
                charts.append(ChartOutput(**result["chart_config"]))
        
        return charts
    
    def _direct_generation_fallback(
        self,
        input_data: ImageCoordinationInput
    ) -> ImageCoordinationOutput:
        """
        Direct chart generation fallback when agent fails.
        """
        from datetime import datetime
        
        charts = []
        for ve in input_data.visualElements:
            result = generate_chart_config_tool(ve.model_dump())
            if result["success"]:
                charts.append(ChartOutput(**result["chart_config"]))
        
        return ImageCoordinationOutput(
            session_id=input_data.session_id,
            id=input_data.id,
            presentation_id=input_data.presentation_id,
            user_id=input_data.user_id,
            generatedCharts=charts,
            chartCount=len(charts),
            timestamp=datetime.utcnow().isoformat() + "Z"
        )


# ==================== CONVENIENCE FUNCTION ====================

def create_image_coordination_agent(
    anthropic_api_key: str,
    **kwargs
) -> ImageCoordinationAgent:
    """
    Factory function to create an Image Coordination Agent.
    
    Args:
        anthropic_api_key: Anthropic API key
        **kwargs: Additional configuration options
        
    Returns:
        ImageCoordinationAgent instance
    """
    return ImageCoordinationAgent(
        anthropic_api_key=anthropic_api_key,
        **kwargs
    )