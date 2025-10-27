"""Document Selection Agent with Zero-shot ReAct and Metadata RAG."""
from typing import Any, Dict, List, Optional
import json
import structlog
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_cohere import ChatCohere

from src.agents.base import BaseAgent, AgentRequest, AgentType
from src.agents.config import get_agent_config
from .prompts import (
    DOCUMENT_SELECTION_SYSTEM_PROMPT,
    METADATA_QUERY_PROMPT,
    DOCUMENT_SCORING_PROMPT,
    REACT_AGENT_TEMPLATE,
    SELECTION_SUMMARY_PROMPT,
)
from .metadata_rag_tool import MetadataRAGTool

logger = structlog.get_logger(__name__)


class DocumentSelectionAgent(BaseAgent):
    """Agent for intelligent document selection using metadata RAG.

    Uses Cohere LLM with Zero-shot ReAct to analyze data requirements
    and select relevant documents from the enterprise corpus.
    """

    def __init__(self):
        """Initialize Document Selection Agent with Cohere and metadata RAG."""
        config = get_agent_config(AgentType.DOCUMENT_SELECTION)
        super().__init__(
            agent_name="document_selection_agent",
            agent_type=AgentType.DOCUMENT_SELECTION,
            config=config,
        )

        # Initialize metadata RAG tool
        self.metadata_tool = MetadataRAGTool()

        # Store agent state
        self.data_requirements: Dict[str, Any] = {}
        self.user_context: Dict[str, Any] = {}
        self.metadata_queries: List[Dict[str, Any]] = []
        self.candidate_documents: List[Dict[str, Any]] = []
        self.selected_documents: List[Dict[str, Any]] = []
        self.tool_call_count = 0

        # Initialize LangChain components
        self._init_langchain_agent()

        self.logger.info(
            "document_selection_agent_initialized",
            langchain_agent_type="ZERO_SHOT_REACT_DESCRIPTION",
            has_metadata_rag=True,
            total_documents_in_corpus=len(self.metadata_tool.document_corpus)
        )

    def _init_langchain_agent(self):
        """Initialize LangChain ReAct agent with Cohere."""
        # Initialize Cohere LLM
        self.llm = ChatCohere(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        # Create tools
        self.tools = self._create_agent_tools()

        # Create ReAct prompt
        react_prompt = PromptTemplate(
            template=REACT_AGENT_TEMPLATE,
            input_variables=["input", "chat_history", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools]),
            },
        )

        # Create ReAct agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=react_prompt,
        )

        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            max_execution_time=30,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def _create_agent_tools(self) -> List[Tool]:
        """Create tools for document selection agent."""
        tools = [
            Tool(
                name="analyze_requirements",
                func=self._tool_analyze_requirements,
                description=(
                    "Analyze data requirements from Conversation Agent to extract key topics, "
                    "document types, departments, and keywords. "
                    "Input: empty string. "
                    "Returns: JSON with extracted query parameters."
                ),
            ),
            Tool(
                name="query_metadata_rag",
                func=self._tool_query_metadata,
                description=(
                    "Query document metadata using topics, departments, doc types, and date ranges. "
                    "Input: JSON with query parameters (key_topics, departments, document_types, date_range, keywords). "
                    "Returns: JSON with matching documents and relevance scores."
                ),
            ),
            Tool(
                name="score_documents",
                func=self._tool_score_documents,
                description=(
                    "Score and rank documents based on relevance to user requirements. "
                    "Input: JSON array of documents to score. "
                    "Returns: Scored and ranked documents with match reasons."
                ),
            ),
            Tool(
                name="finalize_selection",
                func=self._tool_finalize_selection,
                description=(
                    "Finalize document selection and create summary for next agent. "
                    "Input: JSON array of top selected documents. "
                    "Returns: Selection summary with coverage analysis."
                ),
            ),
        ]
        return tools

    def _tool_analyze_requirements(self, input_text: str = "") -> str:
        """Tool: Analyze data requirements to extract query parameters."""
        try:
            self.tool_call_count += 1

            # Format the prompt
            prompt = METADATA_QUERY_PROMPT.format(
                data_requirements=json.dumps(self.data_requirements, indent=2),
                user_context=json.dumps(self.user_context, indent=2),
            )

            # Generate response
            response = self.llm.invoke(prompt)
            query_params = self._parse_json_response(response.content)

            # Store query parameters
            self.metadata_queries.append(query_params)

            self.logger.info(
                "requirements_analyzed",
                key_topics=query_params.get("key_topics", []),
                document_types=query_params.get("document_types", []),
                departments=query_params.get("departments", [])
            )

            return json.dumps(query_params, indent=2)

        except Exception as e:
            self.logger.error("requirement_analysis_failed", error=str(e))
            return json.dumps({"error": str(e), "key_topics": [], "document_types": []})

    def _tool_query_metadata(self, query_params_str: str) -> str:
        """Tool: Query metadata RAG with parameters."""
        try:
            self.tool_call_count += 1

            # Parse query parameters
            if isinstance(query_params_str, str):
                query_params = json.loads(query_params_str)
            else:
                query_params = query_params_str

            # Query metadata RAG
            results = self.metadata_tool.query_metadata(query_params)

            # Parse and store results
            results_dict = json.loads(results)
            self.candidate_documents = results_dict.get("documents", [])

            self.logger.info(
                "metadata_queried",
                total_found=results_dict.get("total_found", 0),
                returned=results_dict.get("returned", 0)
            )

            return results

        except Exception as e:
            self.logger.error("metadata_query_failed", error=str(e))
            return json.dumps({"error": str(e), "documents": []})

    def _tool_score_documents(self, documents_str: str) -> str:
        """Tool: Score and rank documents."""
        try:
            self.tool_call_count += 1

            # Parse documents
            if isinstance(documents_str, str):
                documents = json.loads(documents_str)
            else:
                documents = documents_str

            # If documents is a dict with 'documents' key
            if isinstance(documents, dict) and "documents" in documents:
                documents = documents["documents"]

            # Format prompt
            prompt = DOCUMENT_SCORING_PROMPT.format(
                requirements=json.dumps(self.data_requirements, indent=2),
                documents=json.dumps(documents, indent=2)
            )

            # Generate scoring
            response = self.llm.invoke(prompt)
            scored_docs = self._parse_json_response(response.content)

            # Ensure it's a list
            if isinstance(scored_docs, dict) and "documents" in scored_docs:
                scored_docs = scored_docs["documents"]

            self.logger.info(
                "documents_scored",
                total_scored=len(scored_docs) if isinstance(scored_docs, list) else 0
            )

            return json.dumps(scored_docs, indent=2)

        except Exception as e:
            self.logger.error("document_scoring_failed", error=str(e))
            return json.dumps([])

    def _tool_finalize_selection(self, selected_docs_str: str) -> str:
        """Tool: Finalize selection and create summary."""
        try:
            self.tool_call_count += 1

            # Parse selected documents
            if isinstance(selected_docs_str, str):
                selected_docs = json.loads(selected_docs_str)
            else:
                selected_docs = selected_docs_str

            # Ensure it's a list
            if isinstance(selected_docs, dict):
                if "documents" in selected_docs:
                    selected_docs = selected_docs["documents"]
                elif isinstance(selected_docs, dict) and len(selected_docs) > 0:
                    # Single document in dict format
                    selected_docs = [selected_docs]

            # Take top 10
            top_selections = selected_docs[:10] if isinstance(selected_docs, list) else []

            # Store selected documents
            self.selected_documents = top_selections

            # Create summary
            prompt = SELECTION_SUMMARY_PROMPT.format(
                selected_documents=json.dumps(top_selections, indent=2),
                requirements=json.dumps(self.data_requirements, indent=2)
            )

            response = self.llm.invoke(prompt)
            summary = self._parse_json_response(response.content)

            self.logger.info(
                "selection_finalized",
                total_selected=len(top_selections),
                coverage_percentage=summary.get("requirement_coverage", {}).get("coverage_percentage", 0)
            )

            return json.dumps(summary, indent=2)

        except Exception as e:
            self.logger.error("selection_finalization_failed", error=str(e))
            return json.dumps({
                "total_selected": 0,
                "documents": [],
                "error": str(e)
            })

    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute document selection agent logic.

        Args:
            request: Agent request with data requirements from Conversation Agent

        Returns:
            Dictionary with selected documents
        """
        # Reset state
        self.tool_call_count = 0
        self.metadata_queries = []
        self.candidate_documents = []
        self.selected_documents = []

        # Extract data requirements from context
        context = request.context or {}
        self.data_requirements = context.get("extracted_information", {})
        self.user_context = {
            "user_profile": context.get("user_profile", {}),
            "accessible_documents": context.get("accessible_documents", []),
            "rbac_validation": context.get("rbac_validation", {}),
        }

        self.logger.info(
            "document_selection_started",
            has_requirements=bool(self.data_requirements),
            user_id=self.user_context.get("user_profile", {}).get("userId")
        )

        # Build input for ReAct agent
        input_text = f"""Data requirements from Conversation Agent:

{json.dumps(self.data_requirements, indent=2)}

User Context:
{json.dumps(self.user_context, indent=2)}

Your task: Analyze these requirements and select the most relevant documents from the enterprise corpus.
Use the metadata RAG tools to query and score documents based on relevance.
"""

        try:
            # OPTIMIZED: Use direct metadata query instead of slow ReAct agent
            # The ReAct agent is too slow (60s) and unreliable
            self.logger.info("using_direct_metadata_query_approach")

            # Analyze requirements and build query
            query_params = self._analyze_requirements_simple()

            # Query metadata directly
            import json as json_lib
            results = self.metadata_tool.query_metadata(query_params)
            results_dict = json_lib.loads(results)

            self.candidate_documents = results_dict.get("documents", [])
            self.metadata_queries.append(query_params)
            self.tool_call_count = 1

            self.logger.info(
                "direct_query_completed",
                candidates_found=len(self.candidate_documents),
                query_params=query_params
            )

            # Select top documents
            if self.candidate_documents:
                # Score and select top 10
                self.selected_documents = self._score_and_select_documents(
                    self.candidate_documents
                )
            else:
                # Use fallback mechanism
                self.logger.warning("using_fallback_document_selection")
                self.selected_documents = self._fallback_document_selection()

            agent_output = f"Selected {len(self.selected_documents)} documents using metadata RAG"

            # Build response
            return {
                "selected_documents": self.selected_documents,
                "total_selected": len(self.selected_documents),
                "metadata_queries_made": len(self.metadata_queries),
                "candidate_documents_found": len(self.candidate_documents),
                "tool_calls_made": self.tool_call_count,
                "agent_reasoning": agent_output,
                "next_action": "handoff_to_rag_engine",
                "handoff_to_agent": "RAG Engine",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error("document_selection_failed", error=str(e))

            # Fallback selection
            fallback_docs = self._fallback_document_selection()

            return {
                "selected_documents": fallback_docs,
                "total_selected": len(fallback_docs),
                "metadata_queries_made": 0,
                "candidate_documents_found": 0,
                "tool_calls_made": self.tool_call_count,
                "error": str(e),
                "fallback_used": True,
                "next_action": "handoff_to_rag_engine",
                "handoff_to_agent": "RAG Engine",
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _execute_langchain_agent(self, input_text: str) -> Dict[str, Any]:
        """Execute the LangChain ReAct agent.

        Args:
            input_text: Input for the agent

        Returns:
            Agent execution result
        """
        try:
            result = self.agent_executor.invoke({"input": input_text, "chat_history": ""})

            self.logger.info(
                "langchain_agent_executed",
                tool_calls=self.tool_call_count,
                has_output=bool(result.get("output"))
            )

            return result

        except Exception as e:
            self.logger.error("langchain_agent_error", error=str(e))
            raise

    def _analyze_requirements_simple(self) -> Dict[str, Any]:
        """Simple requirement analysis without LLM.

        Returns:
            Query parameters for metadata RAG
        """
        presentation_reqs = self.data_requirements.get("presentation_requirements", {})
        data_reqs = self.data_requirements.get("data_requirements", {})

        # Extract topics and themes
        key_topics = []
        if "key_themes" in presentation_reqs:
            key_topics.extend(presentation_reqs["key_themes"])
        if "topic" in presentation_reqs:
            key_topics.append(presentation_reqs["topic"])

        # Extract keywords from content needs
        keywords = []
        if "content_to_extract" in data_reqs:
            keywords.extend(data_reqs["content_to_extract"])
        if "specific_metrics" in data_reqs:
            keywords.extend(data_reqs["specific_metrics"])

        # Determine document types (default to financial reports)
        doc_types = ["financial_report", "quarterly_review", "presentation"]

        # Determine departments (default to Finance)
        departments = ["Finance", "Accounting", "Executive"]

        return {
            "key_topics": key_topics,
            "keywords": keywords,
            "document_types": doc_types,
            "departments": departments,
        }

    def _score_and_select_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Score and select top documents.

        Args:
            documents: List of candidate documents

        Returns:
            List of selected documents with scores
        """
        # Simple scoring: documents already have relevance_score from metadata query
        # Sort by relevance and take top 10
        sorted_docs = sorted(
            documents,
            key=lambda x: x.get("relevance_score", 0),
            reverse=True
        )

        selected = sorted_docs[:10]

        # Format for response
        return [
            {
                "document_id": doc["document_id"],
                "document_name": doc["document_name"],
                "doc_type": doc["doc_type"],
                "department": doc["department"],
                "topics": doc["topics"],
                "summary": doc["summary"],
                "relevance_score": doc.get("relevance_score", 50),
                "match_reasons": [
                    f"Matched topics: {', '.join(doc.get('topics', [])[:3])}",
                    f"Department: {doc['department']}",
                    f"Document type: {doc['doc_type']}"
                ]
            }
            for doc in selected
        ]

    def _fallback_document_selection(self) -> List[Dict[str, Any]]:
        """Fallback document selection using simple matching.

        Returns:
            List of selected documents
        """
        self.logger.warning("using_fallback_document_selection")

        # Extract key topics from requirements
        presentation_reqs = self.data_requirements.get("presentation_requirements", {})
        data_reqs = self.data_requirements.get("data_requirements", {})

        topics = presentation_reqs.get("key_themes", [])
        content_needs = data_reqs.get("content_to_extract", [])

        all_topics = topics + content_needs

        # Query by topics
        if all_topics:
            results = self.metadata_tool.query_by_topics(all_topics)
            docs = [r["document"] for r in results[:10]]
        else:
            # Return first 5 documents as ultimate fallback
            docs = self.metadata_tool.document_corpus[:5]

        # Format as selected documents
        return [
            {
                "document_id": doc["document_id"],
                "document_name": doc["document_name"],
                "doc_type": doc["doc_type"],
                "department": doc["department"],
                "topics": doc["topics"],
                "summary": doc["summary"],
                "relevance": "medium",
                "relevance_score": 50,
                "match_reasons": ["Fallback selection based on topic matching"]
            }
            for doc in docs
        ]

    def get_selected_documents_for_next_agent(self) -> Dict[str, Any]:
        """Get formatted selected documents for RAG Engine.

        Returns:
            Dictionary with document selection results
        """
        return {
            "selected_documents": self.selected_documents,
            "total_selected": len(self.selected_documents),
            "data_requirements": self.data_requirements,
            "user_context": self.user_context,
            "metadata_queries": self.metadata_queries,
            "selection_metadata": {
                "tool_calls_made": self.tool_call_count,
                "candidate_documents": len(self.candidate_documents),
                "selection_timestamp": datetime.utcnow().isoformat(),
            }
        }
