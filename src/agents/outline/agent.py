"""Outline Agent - Generate and edit presentation outlines."""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from .prompts import (
    OUTLINE_AGENT_SYSTEM_PROMPT,
    OUTLINE_GENERATION_PROMPT,
    OUTLINE_EDITING_PROMPT,
    REACT_AGENT_TEMPLATE,
    ANALYSIS_PROMPT,
    QUERY_PROCESSING_PROMPT,
    VALIDATION_PROMPT
)

logger = logging.getLogger(__name__)


class OutlineAgent:
    """
    Outline Agent for generating and editing presentation outlines.
    
    Supports two cycle types:
    - generation: Create new outlines from scratch
    - editing: Refine existing outlines based on feedback
    """
    
    def __init__(
        self,
        model_provider: str = "claude",  # "claude" or "openai"
        model_name: str = "claude-sonnet-4-20250514",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        timeout: int = 30,
        max_iterations: int = 10,
        **kwargs
    ):
        """
        Initialize the Outline Agent.
        
        Args:
            model_provider: LLM provider ("claude" or "openai")
            model_name: Specific model name
            temperature: LLM temperature (0.3 for structured output)
            max_tokens: Maximum tokens for response
            timeout: Request timeout in seconds
            max_iterations: Maximum agent iterations
        """
        self.model_provider = model_provider
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_iterations = max_iterations
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize tools
        self.tools = self._create_tools()
        
        # Initialize agent
        self.agent_executor = self._create_agent()
        
        logger.info(
            f"OutlineAgent initialized with {model_provider} ({model_name})"
        )
    
    def _initialize_llm(self):
        """Initialize the LLM based on provider."""
        if self.model_provider == "claude":
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
        elif self.model_provider == "openai":
            return ChatOpenAI(
                model=self.model_name or "gpt-4-turbo-preview",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent."""
        return [
            Tool(
                name="analyze_requirements",
                func=self._analyze_requirements,
                description=(
                    "Analyze presentation requirements, data requirements, and visual preferences. "
                    "Input: JSON with presentationRequirements, dataRequirements, visualPreferences, cycleType. "
                    "Returns: Structured analysis with key themes, objectives, slide distribution."
                )
            ),
            Tool(
                name="process_query_results",
                func=self._process_query_results,
                description=(
                    "Process and organize query results from RAG engine. "
                    "Input: JSON with queryResults array. "
                    "Returns: Query results organized by themes with metrics, insights, trends, and visual opportunities."
                )
            ),
            Tool(
                name="generate_outline",
                func=self._generate_outline,
                description=(
                    "Generate a complete 8-10 slide presentation outline. "
                    "Input: JSON with all requirements and processed query results. "
                    "Returns: Complete outline with slides, bullet points, visual hints, and metadata."
                )
            ),
            Tool(
                name="edit_outline",
                func=self._edit_outline,
                description=(
                    "Edit an existing presentation outline based on feedback. "
                    "Input: JSON with previousOutline, editingContext, requirements, and query results. "
                    "Returns: Updated outline with tracked changes in editingMetadata."
                )
            ),
            Tool(
                name="validate_outline",
                func=self._validate_outline,
                description=(
                    "Validate outline for quality, compliance, and completeness. "
                    "Input: JSON with outline and requirements. "
                    "Returns: Validation results with compliance checks, quality scores, and issues."
                )
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the ReAct agent executor."""
        from langchain.prompts import PromptTemplate
        
        prompt = PromptTemplate(
            template=REACT_AGENT_TEMPLATE,
            input_variables=["input", "tools", "tool_names", "agent_scratchpad"]
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            max_iterations=self.max_iterations,
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def _analyze_requirements(self, input_str: str) -> str:
        """Analyze presentation requirements."""
        try:
            input_data = json.loads(input_str)
            
            prompt = ANALYSIS_PROMPT.format(
                presentation_requirements=json.dumps(input_data.get("presentationRequirements", {}), indent=2),
                data_requirements=json.dumps(input_data.get("dataRequirements", {}), indent=2),
                visual_preferences=json.dumps(input_data.get("visualPreferences", {}), indent=2),
                cycle_type=input_data.get("cycleType", "generation")
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()
            
            # Clean up markdown formatting if present
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            # Validate JSON
            json.loads(result)
            
            logger.info("Requirements analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing requirements: {str(e)}")
            return json.dumps({"error": str(e), "status": "failed"})
    
    def _process_query_results(self, input_str: str) -> str:
        """Process and organize query results."""
        try:
            input_data = json.loads(input_str)
            query_results = input_data.get("queryResults", [])
            synthesized_context = input_data.get("synthesizedContext")

            # If not in input, try to get from stored agent input
            if not synthesized_context and hasattr(self, '_current_agent_input'):
                synthesized_context = self._current_agent_input.get("synthesizedContext")

            synthesized_context = synthesized_context or {}

            # Format query results for prompt
            formatted_results = []
            for qr in query_results:
                formatted_results.append({
                    "queryId": qr.get("queryId"),
                    "answer": qr.get("llmEnhancedAnswer", {}).get("answer"),
                    "confidence": qr.get("llmEnhancedAnswer", {}).get("confidence"),
                    "extractedData": qr.get("llmEnhancedAnswer", {}).get("extractedData", {})
                })

            # Include inter-query insights if available
            inter_query_insights = synthesized_context.get("inter_query_insights", [])
            synthesized_answers = synthesized_context.get("synthesized_answers", {})

            # Build enhanced prompt with synthesis info
            prompt_data = {
                "query_results": formatted_results,
                "inter_query_insights": inter_query_insights,
                "synthesized_answers": synthesized_answers
            }

            prompt = QUERY_PROCESSING_PROMPT.format(
                query_results=json.dumps(prompt_data, indent=2)
            )

            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()

            # Clean up markdown formatting
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()

            # Validate JSON
            json.loads(result)

            logger.info(f"Processed {len(query_results)} query results with {len(inter_query_insights)} insights")
            return result

        except Exception as e:
            logger.error(f"Error processing query results: {str(e)}")
            return json.dumps({"error": str(e), "status": "failed"})
    
    def _generate_outline(self, input_str: str) -> str:
        """Generate presentation outline."""
        try:
            input_data = json.loads(input_str)

            pres_req = input_data.get("presentationRequirements", {})
            data_req = input_data.get("dataRequirements", {})
            visual_pref = input_data.get("visualPreferences", {})
            query_results = input_data.get("processedQueryResults", {})

            # Get synthesizedContext from stored agent input if available
            synthesized_context = {}
            if hasattr(self, '_current_agent_input'):
                synthesized_context = self._current_agent_input.get("synthesizedContext") or {}

            # Extract inter-query insights
            inter_query_insights = synthesized_context.get("inter_query_insights", [])

            # Format inter-query insights as a readable list
            insights_text = "\n".join([f"- {insight}" for insight in inter_query_insights]) if inter_query_insights else "No inter-query insights available."

            prompt = OUTLINE_GENERATION_PROMPT.format(
                topic=pres_req.get("topic", ""),
                target_audience=pres_req.get("targetAudience", "General"),
                num_slides=pres_req.get("numSlides", 10),
                key_themes=json.dumps(pres_req.get("keyThemes", [])),
                tone=pres_req.get("tone", "Professional"),
                objectives=pres_req.get("objectives", ""),
                documents_requested=json.dumps(data_req.get("documentsRequested", [])),
                content_to_extract=json.dumps(data_req.get("contentToExtract", [])),
                metrics=json.dumps(data_req.get("metrics", [])),
                time_periods=json.dumps(data_req.get("timePeriods", [])),
                comparisons=json.dumps(data_req.get("comparisons", [])),
                data_categories=json.dumps(data_req.get("dataCategories", [])),
                chart_types=json.dumps(visual_pref.get("chartTypes", [])),
                style=visual_pref.get("style", "Professional"),
                include_images=visual_pref.get("includeImages", True),
                color_scheme=visual_pref.get("colorScheme", ""),
                query_results_summary=json.dumps(query_results, indent=2),
                inter_query_insights=insights_text
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()
            
            # Clean up markdown formatting
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            # Validate JSON structure
            outline_data = json.loads(result)
            
            # Verify required fields
            if "presentationOutline" not in outline_data:
                raise ValueError("Missing presentationOutline in generated output")
            
            logger.info("Outline generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            return json.dumps({"error": str(e), "status": "failed"})
    
    def _edit_outline(self, input_str: str) -> str:
        """Edit existing presentation outline."""
        try:
            input_data = json.loads(input_str)
            
            previous_outline = input_data.get("previousOutline", {})
            editing_context = input_data.get("editingContext", {})
            pres_req = input_data.get("presentationRequirements", {})
            data_req = input_data.get("dataRequirements", {})
            visual_pref = input_data.get("visualPreferences", {})
            query_results = input_data.get("processedQueryResults", {})
            
            # Extract user feedback from editing context
            user_feedback = editing_context.get("userFeedback", "No specific feedback provided")
            
            prompt = OUTLINE_EDITING_PROMPT.format(
                previous_outline=json.dumps(previous_outline, indent=2),
                user_feedback=user_feedback,
                target_slide_for_edit=editing_context.get("targetSlideForEdit", "null"),
                is_editing=editing_context.get("isEditing", True),
                topic=pres_req.get("topic", ""),
                target_audience=pres_req.get("targetAudience", "General"),
                num_slides=pres_req.get("numSlides", 10),
                key_themes=json.dumps(pres_req.get("keyThemes", [])),
                tone=pres_req.get("tone", "Professional"),
                objectives=pres_req.get("objectives", ""),
                documents_requested=json.dumps(data_req.get("documentsRequested", [])),
                content_to_extract=json.dumps(data_req.get("contentToExtract", [])),
                metrics=json.dumps(data_req.get("metrics", [])),
                time_periods=json.dumps(data_req.get("timePeriods", [])),
                comparisons=json.dumps(data_req.get("comparisons", [])),
                data_categories=json.dumps(data_req.get("dataCategories", [])),
                chart_types=json.dumps(visual_pref.get("chartTypes", [])),
                style=visual_pref.get("style", "Professional"),
                include_images=visual_pref.get("includeImages", True),
                color_scheme=visual_pref.get("colorScheme", ""),
                query_results_summary=json.dumps(query_results, indent=2)
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()
            
            # Clean up markdown formatting
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            # Validate JSON structure
            outline_data = json.loads(result)
            
            # Verify required fields
            if "presentationOutline" not in outline_data:
                raise ValueError("Missing presentationOutline in edited output")
            
            if "outlineMetadata" not in outline_data:
                raise ValueError("Missing outlineMetadata in edited output")
            
            if "editingMetadata" not in outline_data.get("outlineMetadata", {}):
                logger.warning("editingMetadata missing, adding empty metadata")
                outline_data["outlineMetadata"]["editingMetadata"] = {
                    "modifiedSlides": [],
                    "addedSlides": [],
                    "removedSlides": [],
                    "structuralChanges": None
                }
            
            logger.info("Outline edited successfully")
            return json.dumps(outline_data)
            
        except Exception as e:
            logger.error(f"Error editing outline: {str(e)}")
            return json.dumps({"error": str(e), "status": "failed"})
    
    def _validate_outline(self, input_str: str) -> str:
        """Validate outline quality and compliance."""
        try:
            input_data = json.loads(input_str)
            
            outline = input_data.get("outline", {})
            requirements = input_data.get("requirements", {})
            
            prompt = VALIDATION_PROMPT.format(
                outline=json.dumps(outline, indent=2),
                requirements=json.dumps(requirements, indent=2)
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()
            
            # Clean up markdown formatting
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            # Validate JSON
            validation_result = json.loads(result)
            
            logger.info(
                f"Validation completed: isValid={validation_result.get('isValid', False)}"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error validating outline: {str(e)}")
            return json.dumps({"error": str(e), "status": "failed"})
    
    def run(
        self,
        session_id: str,
        user_id: str,
        outline_id: str,
        cycle_type: str,
        extracted_information: Dict[str, Any],
        query_results: List[Dict[str, Any]],
        editing_context: Optional[Dict[str, Any]] = None,
        synthesized_context: Optional[Dict[str, Any]] = None,
        generated_queries: Optional[List[Dict[str, Any]]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the Outline Agent.

        Args:
            session_id: Session identifier
            user_id: User identifier
            outline_id: Outline identifier
            cycle_type: "generation" or "editing"
            extracted_information: User requirements and preferences
            query_results: Results from Query Agent
            editing_context: Context for editing (required if cycle_type is "editing")
            synthesized_context: Synthesized context with inter-query insights
            generated_queries: Generated queries metadata
            performance_metrics: Performance metrics from Query Agent

        Returns:
            Dictionary with outline and metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info(
                f"Starting Outline Agent - Session: {session_id}, "
                f"Cycle: {cycle_type}, Outline: {outline_id}"
            )
            
            # Prepare agent input
            agent_input = {
                "sessionId": session_id,
                "userId": user_id,
                "outlineId": outline_id,
                "cycleType": cycle_type,
                "extractedInformation": extracted_information,
                "queryResults": query_results,
                "synthesizedContext": synthesized_context,
                "generatedQueries": generated_queries or [],
                "performanceMetrics": performance_metrics,
                "editingContext": editing_context or {
                    "isEditing": False,
                    "previousOutline": None,
                    "targetSlideForEdit": None
                }
            }

            # Store in instance variable so tools can access it
            self._current_agent_input = agent_input

            # Extract key info for concise input (to avoid timeouts)
            pres_req = extracted_information.get("presentationRequirements", {})
            topic = pres_req.get("topic", "Unknown")
            num_slides = pres_req.get("numSlides", 10)
            key_themes = pres_req.get("keyThemes", [])

            # Get inter_query_insights if available
            inter_query_insights = []
            if synthesized_context:
                inter_query_insights = synthesized_context.get("inter_query_insights", [])

            # Format input for agent (concise to avoid timeouts)
            input_text = (
                f"Cycle Type: {cycle_type}\n"
                f"Session ID: {session_id}\n"
                f"Outline ID: {outline_id}\n\n"
                f"Presentation Topic: {topic}\n"
                f"Target Slides: {num_slides}\n"
                f"Key Themes: {', '.join(key_themes[:5])}\n\n"
                f"Query Results: {len(query_results)} results available\n"
            )

            if inter_query_insights:
                input_text += f"Inter-Query Insights ({len(inter_query_insights)}):\n"
                for insight in inter_query_insights[:3]:  # Show first 3
                    input_text += f"- {insight}\n"
                input_text += "\n"
            
            if cycle_type == "editing" and editing_context:
                input_text += f"Editing Context:\n{json.dumps(editing_context, indent=2)}\n\n"
            
            input_text += (
                "Your task: Follow the workflow to generate/edit a high-quality presentation outline. "
                "Use the available tools to analyze requirements, process query results, "
                "generate/edit the outline, and validate the result."
            )
            
            # Run agent
            result = self.agent_executor.invoke({"input": input_text})
            
            # Extract outline from agent output
            output = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Try to extract JSON from final answer or tool outputs
            outline_data = self._extract_outline_from_output(output, intermediate_steps)
            
            if not outline_data:
                raise ValueError("Failed to extract valid outline from agent output")
            
            # Add response metadata
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            response = {
                "success": True,
                "sessionId": session_id,
                "userId": user_id,
                "outlineId": outline_id,
                "cycleType": cycle_type,
                "presentationOutline": outline_data.get("presentationOutline", {}),
                "outlineMetadata": outline_data.get("outlineMetadata", {}),
                "qualityChecks": outline_data.get("qualityChecks", {}),
                "nextAction": outline_data.get("nextAction", "proceed_to_content_agent"),
                "handoffToAgent": outline_data.get("handoffToAgent"),
                "performanceMetrics": {
                    "responseTime": response_time,
                    "agentIterations": len(intermediate_steps),
                    "toolCallsMade": len(intermediate_steps)
                },
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
            
            logger.info(
                f"Outline Agent completed successfully in {response_time:.2f}s "
                f"with {len(intermediate_steps)} iterations"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Outline Agent execution failed: {str(e)}", exc_info=True)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "success": False,
                "sessionId": session_id,
                "userId": user_id,
                "outlineId": outline_id,
                "cycleType": cycle_type,
                "presentationOutline": None,
                "outlineMetadata": None,
                "qualityChecks": None,
                "nextAction": "refine_outline",
                "handoffToAgent": None,
                "performanceMetrics": {
                    "responseTime": response_time,
                    "agentIterations": 0,
                    "toolCallsMade": 0
                },
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _extract_outline_from_output(
        self,
        output: str,
        intermediate_steps: List
    ) -> Optional[Dict[str, Any]]:
        """Extract outline JSON from agent output or tool results."""
        # Try to parse output directly
        try:
            # Clean output
            cleaned = output.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            data = json.loads(cleaned)
            if "presentationOutline" in data:
                return self._sanitize_outline(data)
        except:
            pass
        
        # Try to extract from tool outputs (look for generate_outline or edit_outline results)
        for step in reversed(intermediate_steps):
            try:
                action, observation = step
                if action.tool in ["generate_outline", "edit_outline"]:
                    data = json.loads(observation)
                    if "presentationOutline" in data:
                        return self._sanitize_outline(data)
            except:
                continue
        
        return None
    
    def _sanitize_outline(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize and validate outline structure to ensure all required fields are present.
        Fixes common LLM omissions like missing 'purpose' in visualHints.
        """
        try:
            # Ensure presentationOutline exists
            if "presentationOutline" not in outline:
                return outline
            
            pres_outline = outline["presentationOutline"]
            
            # Sanitize each slide
            if "slides" in pres_outline:
                for slide in pres_outline["slides"]:
                    # Ensure visualHints have all required fields
                    if "visualHints" in slide:
                        for visual in slide["visualHints"]:
                            # Add default purpose if missing
                            if "purpose" not in visual or not visual["purpose"]:
                                visual["purpose"] = f"Visualize {visual.get('dataSource', 'data')}"
                            
                            # Ensure visualType is present
                            if "visualType" not in visual:
                                visual["visualType"] = "chart"
                            
                            # Ensure dataSource is present
                            if "dataSource" not in visual:
                                visual["dataSource"] = "unknown"
                    
                    # Ensure bulletPoints have required fields
                    if "bulletPoints" in slide:
                        for bullet in slide["bulletPoints"]:
                            # Ensure requiresData is boolean
                            if "requiresData" not in bullet:
                                bullet["requiresData"] = False
                            
                            # Ensure dataMapping structure
                            if bullet.get("requiresData") and "dataMapping" not in bullet:
                                bullet["dataMapping"] = {
                                    "queryId": None,
                                    "metricName": None,
                                    "dataType": None
                                }
            
            logger.info("Outline sanitized successfully")
            return outline
            
        except Exception as e:
            logger.error(f"Error sanitizing outline: {str(e)}")
            return outline


# Convenience function for easy instantiation
def create_outline_agent(**kwargs) -> OutlineAgent:
    """Create and return an OutlineAgent instance."""
    return OutlineAgent(**kwargs)