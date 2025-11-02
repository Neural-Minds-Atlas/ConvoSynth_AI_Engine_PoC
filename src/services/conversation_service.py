"""Conversation service for handling conversation logic."""

from typing import Dict, Any, Optional
import json

from datetime import datetime

from src.db.repositories import (
    UserRepository,
    ConversationRepository,
    DocumentRepository,
)

from src.db.models import (
    UserDocument,
    ConversationDocument,
    ConversationMessage,
    ExtractedInformation,
    RBACValidation,
)

from src.agents.conversation.agent import ConversationAgent
from src.services.rbac_service import RBACService
from src.services.llm_service import LLMService
from src.schemas.conversation import ConversationRequest, EditingContext
from src.utils.logger import get_logger
from src.utils.security import generate_session_id
from src.utils.exceptions import NotFoundException

logger = get_logger(__name__)


class ConversationService:
    """Service for managing conversations."""

    def __init__(
        self,
        user_repo: UserRepository,
        conversation_repo: ConversationRepository,
        document_repo: DocumentRepository,
        rbac_service: RBACService,
        llm_service: LLMService,
    ):
        """Initialize conversation service.

        Args:
            user_repo: User repository
            conversation_repo: Conversation repository
            document_repo: Document repository
            rbac_service: RBAC service
            llm_service: LLM service
        """
        self.user_repo = user_repo
        self.conversation_repo = conversation_repo
        self.document_repo = document_repo
        self.rbac_service = rbac_service
        self.llm_service = llm_service

    def _snake_to_camel(self, data: Any) -> Any:
        """Convert snake_case dict keys to camelCase recursively.

        Args:
            data: Data to convert (can be dict, list, or primitive)

        Returns:
            Converted data with camelCase keys
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Convert snake_case to camelCase
                camel_key = ''.join(word.capitalize() if i > 0 else word 
                                   for i, word in enumerate(key.split('_')))
                result[camel_key] = self._snake_to_camel(value)
            return result
        elif isinstance(data, list):
            return [self._snake_to_camel(item) for item in data]
        else:
            return data

    async def process_conversation(
        self,
        user_id: str,
        request: ConversationRequest,
    ) -> Dict[str, Any]:
        """Process a conversation request.

        Args:
            user_id: User ID
            request: Conversation request

        Returns:
            Conversation response dictionary

        Raises:
            NotFoundException: If user or session not found
        """
        # Get user
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        # Get or create session
        if request.sessionId:
            conversation = await self.conversation_repo.get_conversation(request.sessionId)
            if not conversation:
                raise NotFoundException("Conversation", request.sessionId)
            session_id = request.sessionId
        else:
            # Create new session
            session_id = generate_session_id()
            conversation = ConversationDocument(
                sessionId=session_id,
                userId=user_id,
                cycleType=request.cycleType,
                messages=[],
                extractedInfo=ExtractedInformation().model_dump(),
                rbacValidation=RBACValidation().model_dump(),
            )
            await self.conversation_repo.create_conversation(conversation)

        # Get accessible documents
        accessible_docs = await self.rbac_service.get_accessible_documents(user.profile)

        # Initialize conversation agent
        agent = ConversationAgent(
            llm_service=self.llm_service,
            rbac_service=self.rbac_service,
            conversation_repo=self.conversation_repo,
            document_repo=self.document_repo,
        )

        # Set context
        agent.set_context(
            user_profile=user.profile,
            accessible_documents=accessible_docs,
            cycle_type=request.cycleType,
            conversation_history=[msg.model_dump() for msg in conversation.messages],
        )

        # Process message
        result = await agent.process_message(
            user_message=request.userMessage,
            session_id=session_id,
        )

        # 🔍 DEBUG: Log what we get from agent
        extracted_info_raw = result.get("extractedInformation", {})
        logger.info("🔍 DEBUG - RAW extracted_info from agent:", 
                   extra={"data": json.dumps(extracted_info_raw, indent=2)})

        # Transform extracted information
        extracted_info_camel = self._snake_to_camel(extracted_info_raw)

        # 🔍 DEBUG: Log after conversion
        logger.info("🔍 DEBUG - AFTER snake_to_camel conversion:", 
                   extra={"data": json.dumps(extracted_info_camel, indent=2)})

        # Update conversation in database
        update_data = {
            "messages": [
                ConversationMessage(**msg).model_dump()
                for msg in result["conversationHistory"]
            ],
            "extractedInfo": extracted_info_camel,
            "rbacValidation": result.get("rbacValidation", {}),
            "nextAction": result.get("nextAction", "continue_conversation"),
            "handoffToAgent": result.get("handoffToAgent"),
            "rbacWarnings": result.get("rbacWarnings", []),
            "suggestedDocuments": result.get("suggestedDocuments", []),
            "totalCallsMade": conversation.totalCallsMade + 1,
            "updatedAt": datetime.utcnow(),
        }

        # 🔍 DEBUG: Log what we're sending to DB
        logger.info("🔍 DEBUG - SENDING TO DB:", 
                   extra={"extractedInfo": json.dumps(update_data["extractedInfo"], indent=2)})

        await self.conversation_repo.update_conversation(session_id, update_data)

        logger.info(
            "conversation_processed",
            session_id=session_id,
            user_id=user_id,
            is_complete=result.get("isComplete", False),
        )

        # Add session ID to result
        result["sessionId"] = session_id
        result["messageId"] = f"msg_{datetime.utcnow().timestamp()}"

        return result

    async def get_session_info(self, session_id: str) -> Optional[ConversationDocument]:
        """Get session information.

        Args:
            session_id: Session ID

        Returns:
            Conversation document if found
        """
        return await self.conversation_repo.get_conversation(session_id)

    async def reset_session(self, session_id: str) -> ConversationDocument:
        """Reset a conversation session.

        Args:
            session_id: Session ID to reset

        Returns:
            Reset conversation document
        """
        return await self.conversation_repo.reset_conversation(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted
        """
        return await self.conversation_repo.delete_conversation(session_id)

    async def get_user_conversations(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        cycle_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get user's conversation history.

        Args:
            user_id: User ID
            skip: Number to skip
            limit: Number to return
            cycle_type: Optional filter by cycle type

        Returns:
            Dictionary with conversations and metadata
        """
        conversations = await self.conversation_repo.get_user_conversations(
            user_id=user_id,
            skip=skip,
            limit=limit,
            cycle_type=cycle_type,
        )

        total_count = await self.conversation_repo.get_conversation_count(
            user_id=user_id,
            cycle_type=cycle_type,
        )

        return {
            "userId": user_id,
            "conversations": [conv.model_dump() for conv in conversations],
            "totalCount": total_count,
            "page": skip // limit + 1,
            "pageSize": limit,
        }