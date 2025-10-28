# ============================================================================
# File: rag_anything/retrieval/financial_retriever.py
# ============================================================================
"""Financial document-specific retrieval logic."""

from typing import Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)


class FinancialRetriever:
    """Retrieves financial information with domain awareness."""
    
    def __init__(self, hybrid_retriever):
        """Initialize financial retriever.
        
        Args:
            hybrid_retriever: HybridRetriever instance
        """
        self.hybrid_retriever = hybrid_retriever
        self.logger = logger.bind(component="financial_retriever")
    
    async def retrieve_financial_data(
        self,
        company: str,
        metric: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Retrieve specific financial data.
        
        Args:
            company: Company name
            metric: Financial metric (revenue, earnings, etc.)
            period: Time period (Q1 2024, FY 2023, etc.)
            **kwargs: Additional retrieval parameters
            
        Returns:
            Retrieved financial data
        """
        # Build financial-specific query
        query = f"{company} {metric} {period}"
        
        self.logger.info("retrieving_financial_data", 
                        company=company, metric=metric, period=period)
        
        result = await self.hybrid_retriever.retrieve(
            query=query,
            mode="hybrid",
            **kwargs
        )
        
        return result
    
    async def retrieve_comparative_data(
        self,
        companies: List[str],
        metric: str,
        period: str
    ) -> Dict[str, Any]:
        """Retrieve comparative data across companies.
        
        Args:
            companies: List of company names
            metric: Financial metric to compare
            period: Time period
            
        Returns:
            Comparative data
        """
        results = {}
        
        for company in companies:
            result = await self.retrieve_financial_data(
                company=company,
                metric=metric,
                period=period
            )
            results[company] = result
        
        return {
            "companies": companies,
            "metric": metric,
            "period": period,
            "data": results
        }