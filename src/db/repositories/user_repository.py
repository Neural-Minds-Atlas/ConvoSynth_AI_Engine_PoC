"""Repository for user operations."""
from typing import Optional, List
from datetime import datetime

from app.db.mongodb import get_collection
from app.db.models import UserDocument, UserProfile
from app.utils.logger import get_logger
from app.utils.exceptions import NotFoundException

logger = get_logger(__name__)


class UserRepository:
    """Repository for user CRUD operations."""

    def __init__(self):
        self.collection = get_collection("users")

    async def create_user(self, user_data: UserDocument) -> UserDocument:
        """Create a new user.

        Args:
            user_data: User document to create

        Returns:
            Created user document
        """
        user_dict = user_data.model_dump()
        user_dict["createdAt"] = datetime.utcnow()
        user_dict["updatedAt"] = datetime.utcnow()

        await self.collection.insert_one(user_dict)

        logger.info(
            "user_created",
            user_id=user_data.userId,
            email=user_data.email,
            role=user_data.profile.role,
        )

        return user_data

    async def get_user_by_id(self, user_id: str) -> Optional[UserDocument]:
        """Get user by user ID.

        Args:
            user_id: User ID to find

        Returns:
            User document if found, None otherwise
        """
        user_dict = await self.collection.find_one({"userId": user_id})
        if user_dict:
            user_dict.pop("_id", None)
            return UserDocument(**user_dict)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserDocument]:
        """Get user by email.

        Args:
            email: Email to find

        Returns:
            User document if found, None otherwise
        """
        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            user_dict.pop("_id", None)
            return UserDocument(**user_dict)
        return None

    async def update_user(self, user_id: str, update_data: dict) -> UserDocument:
        """Update user information.

        Args:
            user_id: User ID to update
            update_data: Fields to update

        Returns:
            Updated user document

        Raises:
            NotFoundException: If user not found
        """
        update_data["updatedAt"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"userId": user_id},
            {"$set": update_data},
            return_document=True,
        )

        if not result:
            raise NotFoundException("User", user_id)

        result.pop("_id", None)
        logger.info("user_updated", user_id=user_id)
        return UserDocument(**result)

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user.

        Args:
            user_id: User ID to delete

        Returns:
            True if deleted, False if not found
        """
        result = await self.collection.delete_one({"userId": user_id})
        deleted = result.deleted_count > 0

        if deleted:
            logger.info("user_deleted", user_id=user_id)

        return deleted

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        department: Optional[str] = None,
        role: Optional[str] = None,
    ) -> List[UserDocument]:
        """List users with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            department: Filter by department
            role: Filter by role

        Returns:
            List of user documents
        """
        query = {}
        if department:
            query["profile.department"] = department
        if role:
            query["profile.role"] = role

        cursor = self.collection.find(query).skip(skip).limit(limit)
        users = []

        async for user_dict in cursor:
            user_dict.pop("_id", None)
            users.append(UserDocument(**user_dict))

        return users

    async def user_exists(self, email: str) -> bool:
        """Check if user exists by email.

        Args:
            email: Email to check

        Returns:
            True if user exists, False otherwise
        """
        count = await self.collection.count_documents({"email": email})
        return count > 0
