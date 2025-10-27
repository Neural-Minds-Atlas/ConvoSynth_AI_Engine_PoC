# ============================================================================
# File: rag_anything/pipeline/content_extractor.py
# ============================================================================
"""Financial content extraction from documents."""

from typing import Dict, Any, List, Optional
import re
import structlog

logger = structlog.get_logger(__name__)


class ContentExtractor:
    """Extracts financial metrics and structured content."""
    
    def __init__(self):
        """Initialize content extractor."""
        self.logger = logger.bind(component="content_extractor")
    
    def extract_financial_metrics(self, content: str) -> Dict[str, Any]:
        """Extract financial metrics from text.
        
        Args:
            content: Document text content
            
        Returns:
            Extracted financial metrics
        """
        metrics = {
            "revenue": [],
            "earnings": [],
            "ebitda": [],
            "profit_margin": [],
            "growth_rate": [],
            "dates": []
        }
        
        try:
            # Extract revenue patterns
            revenue_patterns = [
                r'revenue[s]?\s+(?:of\s+)?\$?([\d,\.]+)\s*([BMK])?',
                r'\$?([\d,\.]+)\s*([BMK])?\s+(?:in\s+)?revenue',
            ]
            
            for pattern in revenue_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    amount = match.group(1).replace(',', '')
                    unit = match.group(2) if match.lastindex > 1 else ''
                    metrics["revenue"].append(f"${amount}{unit}")
            
            # Extract earnings/EPS patterns
            earnings_patterns = [
                r'EPS\s+of\s+\$?([\d,\.]+)',
                r'earnings?\s+(?:per\s+share\s+)?(?:of\s+)?\$?([\d,\.]+)',
            ]
            
            for pattern in earnings_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    metrics["earnings"].append(f"${match.group(1)}")
            
            # Extract EBITDA patterns
            ebitda_pattern = r'EBITDA\s+(?:of\s+)?\$?([\d,\.]+)\s*([BMK])?'
            matches = re.finditer(ebitda_pattern, content, re.IGNORECASE)
            for match in matches:
                amount = match.group(1).replace(',', '')
                unit = match.group(2) if match.lastindex > 1 else ''
                metrics["ebitda"].append(f"${amount}{unit}")
            
            # Extract dates
            date_patterns = [
                r'Q[1-4]\s+\d{4}',
                r'FY\s*\d{4}',
                r'\b\d{4}\b'
            ]
            
            for pattern in date_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    metrics["dates"].append(match.group(0))
            
            # Remove duplicates
            for key in metrics:
                metrics[key] = list(set(metrics[key]))
            
            return metrics
            
        except Exception as e:
            self.logger.error("metric_extraction_failed", error=str(e))
            return metrics
    
    def extract_key_sections(self, content: str) -> Dict[str, str]:
        """Extract key document sections.
        
        Args:
            content: Document content
            
        Returns:
            Dictionary of section name to content
        """
        sections = {}
        
        # Common section headers
        section_patterns = [
            r'(?:Executive\s+)?Summary',
            r'Financial\s+(?:Results|Performance|Highlights)',
            r'Revenue\s+(?:Analysis|Breakdown)',
            r'(?:Outlook|Guidance)',
            r'Risk\s+Factors',
        ]
        
        try:
            for pattern in section_patterns:
                match = re.search(f'({pattern})(.*?)(?=\n[A-Z]|$)', 
                                content, re.IGNORECASE | re.DOTALL)
                if match:
                    section_name = match.group(1).strip()
                    section_content = match.group(2).strip()
                    sections[section_name] = section_content[:1000]  # Limit length
            
        except Exception as e:
            self.logger.error("section_extraction_failed", error=str(e))
        
        return sections
    
    def extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract named entities.
        
        Args:
            content: Document content
            
        Returns:
            Dictionary of entity types to entity lists
        """
        entities = {
            "companies": [],
            "products": [],
            "locations": [],
            "people": []
        }
        
        # Simple pattern-based extraction
        # For production, use NER models like spaCy
        
        return entities
