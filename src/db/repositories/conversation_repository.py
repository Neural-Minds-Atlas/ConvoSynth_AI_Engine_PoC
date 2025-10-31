"""Repository for conversation operations."""
from typing import Optional, List
from datetime import datetime

from src.db.mongodb import get_collection
from src.db.models import ConversationDocument, ConversationMessage
from src.utils.logger import get_logger
from src.utils.exceptions import NotFoundException

logger = get_logger(__name__)


class ConversationRepository:
    """Repository for conversation CRUD operations."""

    def __init__(self):
        self.collection = get_collection("conversations")

    async def create_conversation(
        self,
        conversation_data: ConversationDocument
    ) -> ConversationDocument:
        """Create a new conversation.

        Args:
            conversation_data: Conversation document to create

        Returns:
            Created conversation document
        """
        conv_dict = conversation_data.model_dump()
        conv_dict["createdAt"] = datetime.utcnow()
        conv_dict["updatedAt"] = datetime.utcnow()

        await self.collection.insert_one(conv_dict)

        logger.info(
            "conversation_created",
            session_id=conversation_data.sessionId,
            user_id=conversation_data.userId,
            cycle_type=conversation_data.cycleType,
        )

        return conversation_data

    async def get_conversation(self, session_id: str) -> Optional[ConversationDocument]:
        """Get conversation by session ID.

        Args:
            session_id: Session ID to find

        Returns:
            Conversation document if found, None otherwise
        """
        conv_dict = await self.collection.find_one({"sessionId": session_id})
        if conv_dict:
            conv_dict.pop("_id", None)
            return ConversationDocument(**conv_dict)
        return None

    async def update_conversation(
        self,
        session_id: str,
        update_data: dict
    ) -> ConversationDocument:
        """Update conversation.

        Args:
            session_id: Session ID to update
            update_data: Fields to update

        Returns:
            Updated conversation document

        Raises:
            NotFoundException: If conversation not found
        """
        update_data["updatedAt"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"sessionId": session_id},
            {"$set": update_data},
            return_document=True,
        )

        if not result:
            raise NotFoundException("Conversation", session_id)

        result.pop("_id", None)
        logger.info("conversation_updated", session_id=session_id)
        return ConversationDocument(**result)

    async def add_message(
        self,
        session_id: str,
        message: ConversationMessage
    ) -> ConversationDocument:
        """Add a message to conversation.

        Args:
            session_id: Session ID
            message: Message to add

        Returns:
            Updated conversation document

        Raises:
            NotFoundException: If conversation not found
        """
        result = await self.collection.find_one_and_update(
            {"sessionId": session_id},
            {
                "$push": {"messages": message.model_dump()},
                "$set": {"updatedAt": datetime.utcnow()},
            },
            return_document=True,
        )

        if not result:
            raise NotFoundException("Conversation", session_id)

        result.pop("_id", None)
        return ConversationDocument(**result)

    async def get_user_conversations(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        cycle_type: Optional[str] = None,
        is_complete: Optional[bool] = None,
    ) -> List[ConversationDocument]:
        """Get conversations for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            cycle_type: Filter by cycle type
            is_complete: Filter by completion status

        Returns:
            List of conversation documents
        """
        query = {"userId": user_id}
        if cycle_type:
            query["cycleType"] = cycle_type
        if is_complete is not None:
            query["extractedInfo.isComplete"] = is_complete

        cursor = (
            self.collection.find(query)
            .sort("createdAt", -1)
            .skip(skip)
            .limit(limit)
        )

        conversations = []
        async for conv_dict in cursor:
            conv_dict.pop("_id", None)
            conversations.append(ConversationDocument(**conv_dict))

        return conversations

    async def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        result = await self.collection.delete_one({"sessionId": session_id})
        deleted = result.deleted_count > 0

        if deleted:
            logger.info("conversation_deleted", session_id=session_id)

        return deleted

    async def get_conversation_count(
        self,
        user_id: Optional[str] = None,
        cycle_type: Optional[str] = None,
    ) -> int:
        """Get count of conversations.

        Args:
            user_id: Optional user ID filter
            cycle_type: Optional cycle type filter

        Returns:
            Number of conversations
        """
        query = {}
        if user_id:
            query["userId"] = user_id
        if cycle_type:
            query["cycleType"] = cycle_type

        return await self.collection.count_documents(query)

    async def reset_conversation(self, session_id: str) -> ConversationDocument:
        """Reset conversation state while keeping history.

        Args:
            session_id: Session ID to reset

        Returns:
            Reset conversation document

        Raises:
            NotFoundException: If conversation not found
        """
        from src.db.models import ExtractedInformation, RBACValidation

        reset_data = {
            "extractedInfo": ExtractedInformation().model_dump(),
            "rbacValidation": RBACValidation().model_dump(),
            "nextAction": "continue_conversation",
            "handoffToAgent": None,
            "rbacWarnings": [],
            "suggestedDocuments": [],
            "toolCallsMade": 0,
            "updatedAt": datetime.utcnow(),
        }

        result = await self.collection.find_one_and_update(
            {"sessionId": session_id},
            {"$set": reset_data},
            return_document=True,
        )

        if not result:
            raise NotFoundException("Conversation", session_id)

        result.pop("_id", None)
        logger.info("conversation_reset", session_id=session_id)
        return ConversationDocument(**result)
