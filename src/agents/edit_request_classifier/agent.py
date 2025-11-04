"""
Edit Request Classification Agent
Classifies user edit requests into one of four categories:
1. Visual Edit - HTML/CSS modifications
2. Content Edit - Outline/content regeneration or RAG retrieval
3. CV Edit - Chart/plot/image data changes
4. Regenerate Entire - Full presentation regeneration
"""

import os
from typing import Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from pydantic import BaseModel, Field

from src.agents.edit_request_classifier.prompts import (
    EDIT_CLASSIFIER_SYSTEM_PROMPT,
    CLASSIFICATION_TEMPLATE,
    REQUEST_MODIFIER_TEMPLATE,
    REACT_TEMPLATE
)
from src.utils import get_logger

logger = get_logger(__name__)


class EditClassificationResult(BaseModel):
    """Result of edit request classification"""
    presentation_id: str = Field(..., description="Presentation identifier")
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    edit_request_class: str = Field(
        ..., 
        description="Classification: visual_edit, content_edit, cv_edit, or regenerate_entire"
    )
    modified_user_request: str = Field(
        ..., 
        description="Well-structured prompt with exact changes required"
    )


class EditRequestClassifierAgent:
    """
    Edit Request Classification Agent
    
    Analyzes user edit requests and classifies them into appropriate categories,
    preparing structured prompts for downstream agents.
    """
    
    VALID_CLASSIFICATIONS = [
        "visual_edit",
        "content_edit", 
        "cv_edit",
        "regenerate_entire"
    ]
    
    def __init__(self):
        """Initialize the Edit Request Classifier Agent"""
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.2,  # Low temperature for consistent classification
            max_tokens=2048,
            anthropic_api_key=anthropic_api_key
        )
        
        # Create classification tool
        self.classify_tool = Tool(
            name="classify_edit_request",
            func=self._classify_request,
            description=(
                "Classifies edit request into one of four categories: "
                "visual_edit (HTML/CSS changes), content_edit (outline/content regeneration), "
                "cv_edit (chart/image data changes), regenerate_entire (full regeneration)"
            )
        )
        
        # Create request modifier tool
        self.modify_tool = Tool(
            name="modify_user_request",
            func=self._modify_request,
            description=(
                "Transforms user's raw edit request into a well-structured, "
                "clear prompt that specifies exact changes required"
            )
        )
        
        self.tools = [self.classify_tool, self.modify_tool]
        
        # Create ReAct agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=REACT_TEMPLATE
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True
        )
        
        logger.info("Edit Request Classifier Agent initialized successfully")
    
    def _classify_request(self, user_request: str) -> str:
        """
        Classify the edit request into one of four categories
        
        Args:
            user_request: Raw user edit request
            
        Returns:
            Classification category
        """
        classification_prompt = CLASSIFICATION_TEMPLATE.format(
            user_request=user_request
        )
        
        response = self.llm.invoke(classification_prompt)
        classification = response.content.strip().lower()
        
        # Validate classification
        if classification not in self.VALID_CLASSIFICATIONS:
            # Default to content_edit for safety
            logger.warning(
                f"Invalid classification '{classification}', defaulting to 'content_edit'"
            )
            classification = "content_edit"
        
        logger.info(f"Request classified as: {classification}")
        return classification
    
    def _modify_request(self, user_request: str) -> str:
        """
        Transform raw user request into structured prompt
        
        Args:
            user_request: Raw user edit request
            
        Returns:
            Modified, structured request
        """
        modifier_prompt = REQUEST_MODIFIER_TEMPLATE.format(
            user_request=user_request
        )
        
        response = self.llm.invoke(modifier_prompt)
        modified_request = response.content.strip()
        
        logger.info("User request successfully modified and structured")
        return modified_request
    
    def classify(
        self,
        user_request: str,
        session_id: str,
        presentation_id: str,
        user_id: str
    ) -> EditClassificationResult:
        """
        Classify edit request and prepare structured output
        
        Args:
            user_request: Raw user edit request
            session_id: Session identifier
            presentation_id: Presentation identifier
            user_id: User identifier
            
        Returns:
            EditClassificationResult with classification and modified request
        """
        try:
            logger.info(
                f"Classifying edit request for presentation {presentation_id}, "
                f"session {session_id}"
            )
            
            # Step 1: Classify the request
            classification = self._classify_request(user_request)
            
            # Step 2: Modify and structure the request
            modified_request = self._modify_request(user_request)
            
            # Step 3: Create result
            result = EditClassificationResult(
                presentation_id=presentation_id,
                session_id=session_id,
                user_id=user_id,
                edit_request_class=classification,
                modified_user_request=modified_request
            )
            
            logger.info(
                f"Edit request successfully classified as '{classification}' "
                f"for presentation {presentation_id}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error classifying edit request: {str(e)}")
            # Return safe fallback
            return EditClassificationResult(
                presentation_id=presentation_id,
                session_id=session_id,
                user_id=user_id,
                edit_request_class="content_edit",  # Safe default
                modified_user_request=user_request  # Use original request
            )
    
    async def classify_async(
        self,
        user_request: str,
        session_id: str,
        presentation_id: str,
        user_id: str
    ) -> EditClassificationResult:
        """
        Async version of classify method
        
        Args:
            user_request: Raw user edit request
            session_id: Session identifier
            presentation_id: Presentation identifier
            user_id: User identifier
            
        Returns:
            EditClassificationResult with classification and modified request
        """
        # Since LangChain doesn't have full async support for all operations,
        # we'll use the sync version for now
        # TODO: Implement true async when LangChain has better async support
        return self.classify(user_request, session_id, presentation_id, user_id)