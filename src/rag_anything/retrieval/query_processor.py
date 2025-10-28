# ============================================================================
# File: rag_anything/retrieval/query_processor.py
# ============================================================================
"""Query understanding and preprocessing."""

from typing import Dict, Any, List
import re
import structlog

logger = structlog.get_logger(__name__)


class QueryProcessor:
    """Processes and enriches user queries."""
    
    def __init__(self):
        """Initialize query processor."""
        self.logger = logger.bind(component="query_processor")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process and analyze query.
        
        Args:
            query: User query
            
        Returns:
            Processed query with metadata
        """
        query_lower = query.lower()
        
        processed = {
            "original": query,
            "processed": query,
            "intent": self._detect_intent(query_lower),
            "entities": self._extract_query_entities(query),
            "temporal": self._extract_temporal(query),
            "metric_type": self._detect_metric_type(query_lower)
        }
        
        return processed
    
    def _detect_intent(self, query: str) -> str:
        """Detect query intent.
        
        Args:
            query: Query string
            
        Returns:
            Intent type
        """
        if any(word in query for word in ['compare', 'versus', 'vs']):
            return "comparison"
        elif any(word in query for word in ['trend', 'over time', 'historical']):
            return "trend_analysis"
        elif any(word in query for word in ['summarize', 'summary', 'overview']):
            return "summarization"
        else:
            return "factual"
    
    def _extract_query_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from query.
        
        Args:
            query: Query string
            
        Returns:
            Extracted entities
        """
        entities = {
            "companies": [],
            "metrics": [],
            "periods": []
        }
        
        # Extract company names (basic implementation)
        # For production: use NER model
        
        # Extract periods
        period_patterns = [
            r'Q[1-4]\s*\d{4}',
            r'FY\s*\d{4}',
            r'\d{4}'
        ]
        
        for pattern in period_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["periods"].extend(matches)
        
        return entities
    
    def _extract_temporal(self, query: str) -> Dict[str, Any]:
        """Extract temporal information.
        
        Args:
            query: Query string
            
        Returns:
            Temporal metadata
        """
        temporal = {
            "has_temporal": False,
            "period_type": None,
            "specific_periods": []
        }
        
        # Detect quarter
        if re.search(r'Q[1-4]', query, re.IGNORECASE):
            temporal["has_temporal"] = True
            temporal["period_type"] = "quarter"
        
        # Detect fiscal year
        if re.search(r'FY', query, re.IGNORECASE):
            temporal["has_temporal"] = True
            temporal["period_type"] = "fiscal_year"
        
        return temporal
    
    def _detect_metric_type(self, query: str) -> str:
        """Detect financial metric type.
        
        Args:
            query: Query string
            
        Returns:
            Metric type
        """
        if 'revenue' in query or 'sales' in query:
            return "revenue"
        elif 'earnings' in query or 'eps' in query or 'profit' in query:
            return "earnings"
        elif 'ebitda' in query:
            return "ebitda"
        elif 'margin' in query:
            return "margin"
        elif 'growth' in query:
            return "growth"
        else:
            return "general"