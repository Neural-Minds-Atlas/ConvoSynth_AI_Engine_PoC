# ============================================================================
# File: rag_anything/pipeline/multimodal_analyzer.py
# ============================================================================
"""Multimodal content analysis for charts, tables, and equations."""

from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class MultimodalAnalyzer:
    """Analyzes multimodal content from documents."""
    
    def __init__(self, vision_func: Optional[callable] = None):
        """Initialize multimodal analyzer.
        
        Args:
            vision_func: Vision model function for image analysis
        """
        self.vision_func = vision_func
        self.logger = logger.bind(component="multimodal_analyzer")
    
    async def analyze_image(self, image_data: bytes, context: str = "") -> str:
        """Analyze image content.
        
        Args:
            image_data: Image bytes
            context: Context about the image
            
        Returns:
            Text description of image
        """
        if not self.vision_func:
            return "Image analysis not available"
        
        try:
            prompt = f"Describe this image in detail. Context: {context}"
            description = await self.vision_func(prompt, image_data)
            return description
        except Exception as e:
            self.logger.error("image_analysis_failed", error=str(e))
            return f"Failed to analyze image: {str(e)}"
    
    async def analyze_chart(self, chart_data: bytes) -> Dict[str, Any]:
        """Analyze chart or graph.
        
        Args:
            chart_data: Chart image bytes
            
        Returns:
            Structured chart analysis
        """
        if not self.vision_func:
            return {"error": "Vision model not available"}
        
        try:
            prompt = """Analyze this chart and extract:
            1. Chart type (bar, line, pie, etc.)
            2. Title and labels
            3. Key data points and trends
            4. Any notable patterns or insights
            
            Provide a detailed description."""
            
            analysis = await self.vision_func(prompt, chart_data)
            
            return {
                "type": "chart",
                "analysis": analysis,
                "status": "success"
            }
        except Exception as e:
            self.logger.error("chart_analysis_failed", error=str(e))
            return {"error": str(e), "status": "failed"}
    
    async def analyze_table(self, table_data: str) -> Dict[str, Any]:
        """Analyze table structure and content.
        
        Args:
            table_data: Table text content
            
        Returns:
            Table analysis
        """
        try:
            # Parse table structure
            lines = table_data.strip().split('\n')
            
            return {
                "type": "table",
                "rows": len(lines),
                "content": table_data,
                "status": "success"
            }
        except Exception as e:
            self.logger.error("table_analysis_failed", error=str(e))
            return {"error": str(e), "status": "failed"}
    
    async def extract_equations(self, content: str) -> List[str]:
        """Extract mathematical equations from content.
        
        Args:
            content: Document content
            
        Returns:
            List of extracted equations
        """
        equations = []
        
        # Look for LaTeX-style equations
        import re
        latex_pattern = r'\$\$(.+?)\$\$|\$(.+?)\$'
        matches = re.findall(latex_pattern, content)
        
        for match in matches:
            equation = match[0] or match[1]
            if equation:
                equations.append(equation.strip())
        
        return equations