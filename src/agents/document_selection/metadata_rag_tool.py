"""Metadata RAG Tool for Document Selection Agent."""
from typing import Any, Dict, List
import json
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class MetadataRAGTool:
    """Tool for querying document metadata with RAG capabilities."""

    def __init__(self):
        """Initialize metadata RAG tool with dummy/hardcoded data."""
        self.logger = logger.bind(tool="metadata_rag")

        # Hardcoded document metadata for now
        self.document_corpus = self._initialize_dummy_documents()

        self.logger.info(
            "metadata_rag_tool_initialized",
            total_documents=len(self.document_corpus)
        )

    def _initialize_dummy_documents(self) -> List[Dict[str, Any]]:
        """Initialize dummy document metadata."""
        return [
            {
                "document_id": "DOC-FIN-2024-Q4-001",
                "document_name": "Q4 2024 Financial Performance Report",
                "doc_type": "financial_report",
                "department": "Finance",
                "topics": ["revenue", "expenses", "profit margins", "quarterly performance", "financial analysis"],
                "tags": ["Q4", "2024", "financial", "quarterly", "performance", "revenue", "profit"],
                "summary": "Comprehensive financial analysis for Q4 2024 including revenue breakdown, expense analysis, and profit margins across all business units.",
                "date_range": {"start": "2024-10", "end": "2024-12"},
                "size_mb": 5.2,
                "page_count": 42,
                "created_at": "2024-12-15",
                "access_level": "finance_all",
            },
            {
                "document_id": "DOC-FIN-2024-Q3-002",
                "document_name": "Q3 2024 Revenue Analysis",
                "doc_type": "financial_report",
                "department": "Finance",
                "topics": ["revenue", "sales", "market analysis", "growth metrics"],
                "tags": ["Q3", "2024", "revenue", "sales", "growth"],
                "summary": "Detailed revenue analysis for Q3 2024 with breakdown by product lines, regions, and customer segments.",
                "date_range": {"start": "2024-07", "end": "2024-09"},
                "size_mb": 3.8,
                "page_count": 28,
                "created_at": "2024-09-30",
                "access_level": "finance_all",
            },
            {
                "document_id": "DOC-HR-2024-ANN-003",
                "document_name": "2024 Annual Employee Report",
                "doc_type": "hr_report",
                "department": "HR",
                "topics": ["employee satisfaction", "turnover", "hiring", "workforce metrics"],
                "tags": ["HR", "2024", "employees", "workforce", "hiring"],
                "summary": "Annual HR report covering employee satisfaction surveys, turnover rates, hiring statistics, and workforce demographics.",
                "date_range": {"start": "2024-01", "end": "2024-12"},
                "size_mb": 2.1,
                "page_count": 18,
                "created_at": "2024-11-20",
                "access_level": "hr_management",
            },
            {
                "document_id": "DOC-OPS-2024-Q4-004",
                "document_name": "Q4 Operational Efficiency Metrics",
                "doc_type": "operations_report",
                "department": "Operations",
                "topics": ["efficiency", "productivity", "operational metrics", "cost reduction"],
                "tags": ["operations", "Q4", "efficiency", "productivity", "metrics"],
                "summary": "Operational efficiency analysis for Q4 including productivity metrics, cost reduction initiatives, and process improvements.",
                "date_range": {"start": "2024-10", "end": "2024-12"},
                "size_mb": 4.5,
                "page_count": 35,
                "created_at": "2024-12-10",
                "access_level": "operations_all",
            },
            {
                "document_id": "DOC-MKT-2024-Q4-005",
                "document_name": "Q4 Marketing Campaign Analysis",
                "doc_type": "marketing_report",
                "department": "Marketing",
                "topics": ["marketing campaigns", "customer acquisition", "ROI", "brand awareness"],
                "tags": ["marketing", "Q4", "campaigns", "ROI", "customer acquisition"],
                "summary": "Analysis of Q4 marketing campaigns including customer acquisition costs, ROI metrics, and brand awareness studies.",
                "date_range": {"start": "2024-10", "end": "2024-12"},
                "size_mb": 3.2,
                "page_count": 25,
                "created_at": "2024-12-05",
                "access_level": "marketing_all",
            },
            {
                "document_id": "DOC-FIN-2024-BUDGET-006",
                "document_name": "2025 Budget Planning Document",
                "doc_type": "financial_planning",
                "department": "Finance",
                "topics": ["budget", "planning", "forecast", "resource allocation"],
                "tags": ["2025", "budget", "planning", "forecast", "finance"],
                "summary": "2025 budget planning document with departmental allocations, revenue forecasts, and strategic initiatives.",
                "date_range": {"start": "2025-01", "end": "2025-12"},
                "size_mb": 6.8,
                "page_count": 58,
                "created_at": "2024-11-15",
                "access_level": "finance_executive",
            },
            {
                "document_id": "DOC-FIN-2024-ANNUAL-007",
                "document_name": "2024 Annual Financial Summary",
                "doc_type": "financial_report",
                "department": "Finance",
                "topics": ["annual report", "financial summary", "year-end", "performance"],
                "tags": ["2024", "annual", "financial", "summary", "year-end"],
                "summary": "Complete 2024 annual financial summary including all quarters, year-over-year comparisons, and strategic insights.",
                "date_range": {"start": "2024-01", "end": "2024-12"},
                "size_mb": 8.5,
                "page_count": 75,
                "created_at": "2024-12-20",
                "access_level": "finance_all",
            },
            {
                "document_id": "DOC-SALES-2024-Q4-008",
                "document_name": "Q4 Sales Performance Report",
                "doc_type": "sales_report",
                "department": "Sales",
                "topics": ["sales performance", "deals closed", "pipeline", "quotas"],
                "tags": ["sales", "Q4", "performance", "deals", "quotas"],
                "summary": "Q4 sales performance including deals closed, pipeline analysis, quota attainment, and territory performance.",
                "date_range": {"start": "2024-10", "end": "2024-12"},
                "size_mb": 4.1,
                "page_count": 32,
                "created_at": "2024-12-12",
                "access_level": "sales_all",
            },
            {
                "document_id": "DOC-TECH-2024-Q4-009",
                "document_name": "Q4 Technology Infrastructure Report",
                "doc_type": "technical_report",
                "department": "Technology",
                "topics": ["infrastructure", "systems", "uptime", "tech stack", "performance"],
                "tags": ["technology", "infrastructure", "Q4", "systems", "uptime"],
                "summary": "Q4 technology infrastructure report covering system uptime, performance metrics, and infrastructure improvements.",
                "date_range": {"start": "2024-10", "end": "2024-12"},
                "size_mb": 3.5,
                "page_count": 28,
                "created_at": "2024-12-08",
                "access_level": "tech_all",
            },
            {
                "document_id": "DOC-FIN-2023-Q4-010",
                "document_name": "Q4 2023 Financial Performance Report",
                "doc_type": "financial_report",
                "department": "Finance",
                "topics": ["revenue", "expenses", "quarterly performance", "year-over-year"],
                "tags": ["Q4", "2023", "financial", "quarterly", "historical"],
                "summary": "Q4 2023 financial performance report for year-over-year comparison purposes.",
                "date_range": {"start": "2023-10", "end": "2023-12"},
                "size_mb": 4.8,
                "page_count": 38,
                "created_at": "2023-12-18",
                "access_level": "finance_all",
            },
        ]

    def query_by_topics(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Query documents by topics.

        Args:
            topics: List of topics to search for

        Returns:
            List of matching documents with scores
        """
        matching_docs = []
        topics_lower = [t.lower() for t in topics]

        for doc in self.document_corpus:
            doc_topics = [t.lower() for t in doc.get("topics", [])]
            doc_tags = [t.lower() for t in doc.get("tags", [])]

            # Count matches
            topic_matches = len(set(topics_lower) & set(doc_topics))
            tag_matches = len(set(topics_lower) & set(doc_tags))

            total_matches = topic_matches + (tag_matches * 0.5)

            if total_matches > 0:
                matching_docs.append({
                    "document": doc,
                    "topic_match_score": total_matches,
                    "matched_topics": list(set(topics_lower) & set(doc_topics)),
                    "matched_tags": list(set(topics_lower) & set(doc_tags)),
                })

        # Sort by match score
        matching_docs.sort(key=lambda x: x["topic_match_score"], reverse=True)

        self.logger.info(
            "topic_query_completed",
            topics=topics,
            matches_found=len(matching_docs)
        )

        return matching_docs

    def query_by_department(self, departments: List[str]) -> List[Dict[str, Any]]:
        """Query documents by department.

        Args:
            departments: List of departments

        Returns:
            List of matching documents
        """
        matching_docs = []
        departments_lower = [d.lower() for d in departments]

        for doc in self.document_corpus:
            if doc.get("department", "").lower() in departments_lower:
                matching_docs.append({"document": doc})

        self.logger.info(
            "department_query_completed",
            departments=departments,
            matches_found=len(matching_docs)
        )

        return matching_docs

    def query_by_doc_type(self, doc_types: List[str]) -> List[Dict[str, Any]]:
        """Query documents by document type.

        Args:
            doc_types: List of document types

        Returns:
            List of matching documents
        """
        matching_docs = []
        doc_types_lower = [dt.lower() for dt in doc_types]

        for doc in self.document_corpus:
            if doc.get("doc_type", "").lower() in doc_types_lower:
                matching_docs.append({"document": doc})

        self.logger.info(
            "doc_type_query_completed",
            doc_types=doc_types,
            matches_found=len(matching_docs)
        )

        return matching_docs

    def query_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Query documents by date range.

        Args:
            start_date: Start date in YYYY-MM format
            end_date: End date in YYYY-MM format

        Returns:
            List of matching documents
        """
        matching_docs = []

        for doc in self.document_corpus:
            doc_range = doc.get("date_range", {})
            doc_start = doc_range.get("start", "")
            doc_end = doc_range.get("end", "")

            # Check if date ranges overlap
            if doc_start and doc_end:
                if doc_start <= end_date and doc_end >= start_date:
                    matching_docs.append({"document": doc})

        self.logger.info(
            "date_range_query_completed",
            start=start_date,
            end=end_date,
            matches_found=len(matching_docs)
        )

        return matching_docs

    def query_metadata(self, query_params: Dict[str, Any]) -> str:
        """Main metadata query function for tool use.

        Args:
            query_params: Dictionary with query parameters

        Returns:
            JSON string of matching documents
        """
        try:
            # Parse query parameters
            topics = query_params.get("key_topics", [])
            departments = query_params.get("departments", [])
            doc_types = query_params.get("document_types", [])
            date_range = query_params.get("date_range", {})
            keywords = query_params.get("keywords", [])

            # Combine topics and keywords
            all_search_terms = topics + keywords

            # Start with all documents
            candidate_docs = self.document_corpus.copy()

            # Filter by department if specified
            if departments:
                dept_results = self.query_by_department(departments)
                dept_ids = {d["document"]["document_id"] for d in dept_results}
                candidate_docs = [
                    doc for doc in candidate_docs
                    if doc["document_id"] in dept_ids
                ]

            # Filter by doc type if specified
            if doc_types:
                type_results = self.query_by_doc_type(doc_types)
                type_ids = {d["document"]["document_id"] for d in type_results}
                candidate_docs = [
                    doc for doc in candidate_docs
                    if doc["document_id"] in type_ids
                ]

            # Filter by date range if specified
            if date_range and date_range.get("start") and date_range.get("end"):
                date_results = self.query_by_date_range(
                    date_range["start"],
                    date_range["end"]
                )
                date_ids = {d["document"]["document_id"] for d in date_results}
                candidate_docs = [
                    doc for doc in candidate_docs
                    if doc["document_id"] in date_ids
                ]

            # Score by topic/keyword match
            scored_docs = []
            if all_search_terms:
                for doc in candidate_docs:
                    topics_lower = [t.lower() for t in all_search_terms]
                    doc_topics = [t.lower() for t in doc.get("topics", [])]
                    doc_tags = [t.lower() for t in doc.get("tags", [])]
                    doc_summary = doc.get("summary", "").lower()

                    topic_matches = len(set(topics_lower) & set(doc_topics))
                    tag_matches = len(set(topics_lower) & set(doc_tags))
                    summary_matches = sum(
                        1 for term in topics_lower if term in doc_summary
                    )

                    total_score = (
                        topic_matches * 3.0 +
                        tag_matches * 1.5 +
                        summary_matches * 1.0
                    )

                    if total_score > 0:
                        scored_docs.append({
                            "document": doc,
                            "relevance_score": total_score,
                            "topic_matches": topic_matches,
                            "tag_matches": tag_matches,
                            "summary_matches": summary_matches,
                        })
            else:
                # No search terms, return all candidates
                scored_docs = [
                    {"document": doc, "relevance_score": 1.0}
                    for doc in candidate_docs
                ]

            # Sort by relevance
            scored_docs.sort(key=lambda x: x["relevance_score"], reverse=True)

            # Return top 15 documents
            top_docs = scored_docs[:15]

            result = {
                "total_found": len(scored_docs),
                "returned": len(top_docs),
                "documents": [
                    {
                        "document_id": d["document"]["document_id"],
                        "document_name": d["document"]["document_name"],
                        "doc_type": d["document"]["doc_type"],
                        "department": d["document"]["department"],
                        "topics": d["document"]["topics"],
                        "tags": d["document"]["tags"],
                        "summary": d["document"]["summary"],
                        "date_range": d["document"]["date_range"],
                        "relevance_score": d["relevance_score"],
                    }
                    for d in top_docs
                ]
            }

            self.logger.info(
                "metadata_query_completed",
                total_found=len(scored_docs),
                returned=len(top_docs),
                query_params=query_params
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            self.logger.error("metadata_query_failed", error=str(e))
            return json.dumps({"error": str(e), "documents": []})

    def get_document_by_id(self, document_id: str) -> Dict[str, Any]:
        """Get full document metadata by ID.

        Args:
            document_id: Document identifier

        Returns:
            Document metadata or None
        """
        for doc in self.document_corpus:
            if doc["document_id"] == document_id:
                return doc
        return None
