"""Query Agent - Responsible for RAG retrieval and context enhancement."""

import json
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import structlog
import httpx
from langchain.agents import AgentExecutor, create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

from src.agents.base import BaseAgent, AgentRequest, AgentResponse
from src.agents.query.prompts import (
    QUERY_AGENT_SYSTEM_PROMPT,
    QUERY_GENERATION_PROMPT,
    CONTEXT_SYNTHESIS_PROMPT,
    REACT_AGENT_TEMPLATE,
)


class QueryAgent(BaseAgent):
    """
    Query Agent - Transforms user requirements into RAG queries and synthesizes context.
    
    Responsibilities:
    1. Analyze extracted information from Conversation Agent
    2. Generate targeted queries for RAG engine
    3. Retrieve relevant context from documents
    4. Synthesize retrieved chunks into coherent answers
    5. Maintain inter-query context for token efficiency
    """
    
    def __init__(self, rag_endpoint: Optional[str] = None):
        """
        Initialize Query Agent.

        Args:
            rag_endpoint: URL endpoint for RAG retrieval API
        """
        super().__init__(agent_name="query_agent")
        self.logger = structlog.get_logger(__name__).bind(agent=self.agent_name)
        
        # RAG configuration
        self.rag_endpoint = rag_endpoint or "http://localhost:8000/api/v1/query"
        
        # LLM configuration - Claude 4 Sonnet for superior retrieval
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.1,  # Low temperature for precise queries
            max_tokens=4000,
        )
        
        # Agent state
        self.data_requirements: Dict[str, Any] = {}
        self.generated_queries: List[Dict[str, Any]] = []
        self.retrieved_contexts: List[Dict[str, Any]] = []
        self.synthesized_context: Dict[str, Any] = {}
        self.tool_call_count = 0
        
        # Performance tracking
        self.performance_metrics = {
            "query_generation_time": 0,
            "retrieval_time": 0,
            "synthesis_time": 0,
            "total_tokens_retrieved": 0,
            "total_queries_generated": 0,
        }

        self.logger.info("query_agent_initialized", rag_endpoint=self.rag_endpoint)

    def _determine_rag_mode(self, query_type: str, query_context: Dict[str, Any]) -> Literal["hybrid", "naive", "local", "global"]:
        """
        Determine the optimal RAG retrieval mode based on query type and context.

        Args:
            query_type: Type of query (e.g., "topic", "metric", "comparison", "temporal")
            query_context: Additional context about the query

        Returns:
            RAG mode: "hybrid", "naive", "local", or "global"
        """
        # Global mode: For high-level summaries and overviews
        if query_type in ["overview", "summary", "executive_summary"]:
            return "global"

        # Local mode: For relationship-based queries
        if query_type in ["comparison", "relationship", "dependency"]:
            return "local"

        # Naive mode: For specific fact retrieval or precise information
        if query_type in ["metric", "specific_fact", "definition", "kpi"]:
            return "naive"

        # Hybrid mode (default): Combines vector search + knowledge graph
        # Best for: topic exploration, thematic queries, multi-faceted questions
        return "hybrid"

    def _determine_top_k(self, query_type: str, priority: str) -> int:
        """
        Determine the optimal number of results to retrieve based on query characteristics.

        Args:
            query_type: Type of query
            priority: Priority level ("high", "medium", "low")

        Returns:
            Number of results to retrieve (top_k)
        """
        # High priority or complex queries: retrieve more context
        if priority == "high":
            if query_type in ["topic", "thematic", "comparison"]:
                return 10  # Complex queries need more context
            else:
                return 7

        # Medium priority
        if priority == "medium":
            if query_type in ["metric", "specific_fact"]:
                return 3  # Precise queries need fewer results
            else:
                return 5  # Default for most queries

        # Low priority or supplementary queries
        return 3

    def _generate_system_prompt(self, query_type: str, data_requirements: Dict[str, Any]) -> str:
        """
        Generate a tailored system prompt based on query type and requirements.

        Args:
            query_type: Type of query
            data_requirements: Data requirements from extracted information

        Returns:
            System prompt string
        """
        base_prompt = "You are a specialized AI assistant that extracts information based STRICTLY on the provided context."

        # Customize based on query type
        if query_type == "metric" or query_type == "kpi":
            return (
                f"{base_prompt} Focus on extracting numerical data, metrics, KPIs, and quantitative information. "
                "Include specific numbers, percentages, and measurements."
            )

        elif query_type == "comparison":
            return (
                f"{base_prompt} Focus on comparative analysis, differences, and similarities. "
                "Highlight contrasts, trends, and relative performance."
            )

        elif query_type == "temporal" or query_type == "time_series":
            time_periods = data_requirements.get("timePeriods", [])
            periods_str = ", ".join(time_periods) if time_periods else "specified time periods"
            return (
                f"{base_prompt} Focus on temporal data and trends across {periods_str}. "
                "Extract time-bound information, progression, and chronological data."
            )

        elif query_type == "thematic" or query_type == "topic":
            return (
                f"{base_prompt} Focus on thematic content, key concepts, and topical information. "
                "Extract relevant themes, ideas, and subject matter."
            )

        elif query_type == "overview" or query_type == "summary":
            return (
                f"{base_prompt} Focus on high-level summaries and overview information. "
                "Extract key takeaways, main points, and executive-level insights."
            )

        # Default prompt
        return base_prompt

    def _setup_tools(self) -> List[Tool]:
        """Setup tools for Query Agent."""
        return [
            Tool(
                name="generate_rag_queries",
                func=self._tool_generate_queries,
                description=(
                    "Generate targeted queries for RAG retrieval based on user requirements. "
                    "Input: 'analyze' to generate queries from extracted information. "
                    "Returns: List of generated queries with metadata."
                )
            ),
            Tool(
                name="retrieve_from_rag",
                func=self._tool_retrieve_from_rag,
                description=(
                    "Retrieve relevant context from RAG engine using a specific query. "
                    "Intelligently selects RAG mode (hybrid/naive/local/global), top_k, and system prompt. "
                    "Input: JSON string with 'query', 'query_type' (e.g., 'metric', 'comparison', 'topic'), "
                    "'priority' ('high', 'medium', 'low'), and optional 'filters'. "
                    "Returns: Retrieved context chunks with metadata including mode and retrieval stats."
                )
            ),
            Tool(
                name="synthesize_context",
                func=self._tool_synthesize_context,
                description=(
                    "Synthesize all retrieved contexts into coherent answers. "
                    "Input: 'synthesize' to process all retrieved contexts. "
                    "Returns: Synthesized context organized by topic."
                )
            ),
        ]
    
    def _tool_generate_queries(self, input_text: str = "analyze") -> str:
        """
        Tool: Generate RAG queries from data requirements.

        Analyzes data requirements and creates targeted queries for:
        - Documents requested
        - Content to extract
        - Metric/KPI queries
        - Time period queries
        - Comparison queries
        """
        try:
            self.tool_call_count += 1
            start_time = datetime.utcnow()

            # Build context for query generation using only data requirements
            context = {
                "documents_requested": self.data_requirements.get("documentsRequested", []),
                "content_to_extract": self.data_requirements.get("contentToExtract", []),
                "metrics": self.data_requirements.get("metrics", []),
                "time_periods": self.data_requirements.get("timePeriods", []),
                "comparisons": self.data_requirements.get("comparisons", []),
                "data_categories": self.data_requirements.get("dataCategories", []),
            }

            # Generate queries using LLM
            prompt = QUERY_GENERATION_PROMPT.format(
                data_requirements=json.dumps(context, indent=2)
            )
            
            response = self.llm.invoke(prompt)
            queries_json = response.content.strip()
            
            # Clean JSON markers
            queries_json = queries_json.replace("```json", "").replace("```", "").strip()
            
            # Parse queries
            queries = json.loads(queries_json)
            self.generated_queries = queries.get("queries", [])
            
            # Update metrics
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            self.performance_metrics["query_generation_time"] = generation_time
            self.performance_metrics["total_queries_generated"] = len(self.generated_queries)
            
            self.logger.info(
                "queries_generated",
                count=len(self.generated_queries),
                generation_time=generation_time,
                query_types=[q.get("query_type") for q in self.generated_queries]
            )
            
            return json.dumps({
                "success": True,
                "queries_generated": len(self.generated_queries),
                "queries": self.generated_queries,
                "generation_time": generation_time
            }, indent=2)
            
        except Exception as e:
            self.logger.error("query_generation_failed", error=str(e))
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    def _tool_retrieve_from_rag(self, input_json: str) -> str:
        """
        Tool: Retrieve context from RAG engine using actual API endpoint.

        Intelligently determines RAG parameters (mode, top_k, system_prompt)
        based on query type and makes API call to retrieve context.
        """
        try:
            self.tool_call_count += 1
            start_time = datetime.utcnow()

            # Parse input
            if isinstance(input_json, str):
                retrieval_params = json.loads(input_json)
            else:
                retrieval_params = input_json

            query = retrieval_params.get("query")
            query_type = retrieval_params.get("query_type", "general")
            priority = retrieval_params.get("priority", "medium")
            filters = retrieval_params.get("filters", {})

            # Intelligently determine RAG parameters
            mode = self._determine_rag_mode(query_type, retrieval_params)
            top_k = self._determine_top_k(query_type, priority)
            system_prompt = self._generate_system_prompt(
                query_type,
                self.data_requirements
            )

            # Prepare RAG API request
            rag_request = {
                "query": query,
                "mode": mode,
                "top_k": top_k,
                "use_llm_enhancement": False,  # Always False to get raw context
                "system_prompt": system_prompt
            }

            self.logger.info(
                "rag_retrieval_started",
                query=query,
                mode=mode,
                top_k=top_k,
                query_type=query_type,
                priority=priority
            )

            # Make actual API call to RAG endpoint
            import asyncio
            retrieved_data = asyncio.run(self._call_rag_api(rag_request))

            # Extract chunks from response (ChatResponse returns "context", not "results")
            retrieved_chunks = retrieved_data.get("context", [])

            # Store retrieved context with metadata
            # Note: ContextChunk doesn't have token_count, so we estimate: ~4 chars per token
            total_tokens = sum(len(chunk.get("content", "")) // 4 for chunk in retrieved_chunks)

            context_entry = {
                "query": query,
                "query_type": query_type,
                "mode": mode,
                "top_k": top_k,
                "priority": priority,
                "filters": filters,
                "chunks": retrieved_chunks,
                "retrieved_at": datetime.utcnow().isoformat(),
                "chunk_count": len(retrieved_chunks),
                "total_tokens": total_tokens,
                "rag_metadata": retrieved_data.get("metadata", {})
            }
            self.retrieved_contexts.append(context_entry)

            # Update metrics
            retrieval_time = (datetime.utcnow() - start_time).total_seconds()
            self.performance_metrics["retrieval_time"] += retrieval_time
            self.performance_metrics["total_tokens_retrieved"] += context_entry["total_tokens"]

            self.logger.info(
                "rag_retrieval_completed",
                chunks_retrieved=len(retrieved_chunks),
                total_tokens=context_entry["total_tokens"],
                retrieval_time=retrieval_time,
                mode=mode
            )

            return json.dumps({
                "success": True,
                "chunks_retrieved": len(retrieved_chunks),
                "total_tokens": context_entry["total_tokens"],
                "retrieval_time": retrieval_time,
                "mode": mode,
                "top_k": top_k
            }, indent=2)

        except Exception as e:
            self.logger.error("rag_retrieval_failed", error=str(e), error_type=type(e).__name__)
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    async def _call_rag_api(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make async HTTP call to RAG retrieval endpoint.

        Args:
            request_payload: Request payload containing query, mode, top_k, etc.

        Returns:
            RAG API response with retrieved chunks and metadata

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.rag_endpoint,
                    json=request_payload
                )
                response.raise_for_status()

                data = response.json()

                self.logger.debug(
                    "rag_api_call_successful",
                    status_code=response.status_code,
                    results_count=len(data.get("context", []))
                )

                return data

        except httpx.HTTPError as e:
            self.logger.error(
                "rag_api_call_failed",
                error=str(e),
                status_code=getattr(e.response, 'status_code', None)
            )
            raise
        except Exception as e:
            self.logger.error("rag_api_unexpected_error", error=str(e))
            raise
    
    def _tool_synthesize_context(self, input_text: str = "synthesize") -> str:
        """
        Tool: Synthesize all retrieved contexts into coherent answers.
        
        Takes all retrieved RAG chunks and creates organized, query-specific answers
        while maintaining inter-query context.
        """
        try:
            self.tool_call_count += 1
            start_time = datetime.utcnow()
            
            if not self.retrieved_contexts:
                return json.dumps({
                    "success": False,
                    "error": "No contexts retrieved yet. Call retrieve_from_rag first."
                })
            
            # Organize contexts by query
            organized_contexts = {}
            for idx, query_info in enumerate(self.generated_queries):
                query_text = query_info.get("query")
                query_type = query_info.get("query_type")
                
                # Find corresponding retrieved context
                if idx < len(self.retrieved_contexts):
                    context_entry = self.retrieved_contexts[idx]
                    organized_contexts[query_text] = {
                        "query_type": query_type,
                        "priority": query_info.get("priority"),
                        "chunks": context_entry.get("chunks", []),
                        "chunk_count": context_entry.get("chunk_count", 0)
                    }
            
            # Build synthesis prompt
            prompt = CONTEXT_SYNTHESIS_PROMPT.format(
                data_requirements=json.dumps(self.data_requirements, indent=2),
                retrieved_contexts=json.dumps(organized_contexts, indent=2)
            )
            
            # Synthesize using LLM
            response = self.llm.invoke(prompt)
            synthesis_json = response.content.strip()
            
            # Clean JSON markers
            synthesis_json = synthesis_json.replace("```json", "").replace("```", "").strip()
            
            # Parse synthesis
            self.synthesized_context = json.loads(synthesis_json)
            
            # Update metrics
            synthesis_time = (datetime.utcnow() - start_time).total_seconds()
            self.performance_metrics["synthesis_time"] = synthesis_time
            
            self.logger.info(
                "context_synthesized",
                synthesis_time=synthesis_time,
                topics_synthesized=len(self.synthesized_context.get("synthesized_answers", {}))
            )
            
            return json.dumps({
                "success": True,
                "synthesis_time": synthesis_time,
                "topics_synthesized": len(self.synthesized_context.get("synthesized_answers", {}))
            }, indent=2)
            
        except Exception as e:
            self.logger.error("context_synthesis_failed", error=str(e))
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    async def _execute(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute Query Agent logic."""
        try:
            # Extract data requirements from request
            context = request.context or {}
            self.data_requirements = context.get("dataRequirements", {})

            if not self.data_requirements:
                return {
                    "success": False,
                    "error": "No data requirements provided",
                    "message": "dataRequirements is required in context"
                }
            
            # Setup tools and agent
            tools = self._setup_tools()
            
            # Create ReAct agent
            prompt = PromptTemplate.from_template(REACT_AGENT_TEMPLATE)
            
            agent = create_react_agent(
                llm=self.llm,
                tools=tools,
                prompt=prompt
            )
            
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=15,
                return_intermediate_steps=True
            )
            
            # Execute agent with system prompt context
            input_text = f"""
{QUERY_AGENT_SYSTEM_PROMPT}

DATA REQUIREMENTS FROM CONVERSATION AGENT:
{json.dumps(self.data_requirements, indent=2)}

Your task:
1. Generate targeted RAG queries using generate_rag_queries based on data requirements
2. Retrieve context for each query using retrieve_from_rag
3. Synthesize all contexts using synthesize_context
4. Provide final enhanced context for downstream agents
"""
            
            result = await agent_executor.ainvoke({
                "input": input_text,
                "agent_scratchpad": ""
            })
            
            output_text = result.get("output", "")
            
            return {
                "success": True,
                "response": output_text,
                "generated_queries": self.generated_queries,
                "retrieved_contexts": self.retrieved_contexts,
                "synthesized_context": self.synthesized_context,
                "performance_metrics": self.performance_metrics,
                "tool_calls_made": self.tool_call_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error("query_agent_execution_failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "partial_results": {
                    "generated_queries": self.generated_queries,
                    "retrieved_contexts": self.retrieved_contexts,
                }
            }
    
    def reset(self):
        """Reset agent state."""
        self.data_requirements = {}
        self.generated_queries = []
        self.retrieved_contexts = []
        self.synthesized_context = {}
        self.tool_call_count = 0
        self.performance_metrics = {
            "query_generation_time": 0,
            "retrieval_time": 0,
            "synthesis_time": 0,
            "total_tokens_retrieved": 0,
            "total_queries_generated": 0,
        }
        self.logger.info("query_agent_reset")