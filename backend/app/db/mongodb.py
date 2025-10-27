"""MongoDB connection and database management."""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Global MongoDB client
_mongodb_client: Optional[AsyncIOMotorClient] = None
_mongodb_database: Optional[AsyncIOMotorDatabase] = None


async def init_db() -> None:
    """Initialize MongoDB connection."""
    global _mongodb_client, _mongodb_database

    try:
        logger.info(
            "initializing_mongodb",
            uri=settings.mongodb_uri,
            database=settings.mongodb_db_name,
        )

        _mongodb_client = AsyncIOMotorClient(
            settings.mongodb_uri,
            minPoolSize=settings.mongodb_min_pool_size,
            maxPoolSize=settings.mongodb_max_pool_size,
            serverSelectionTimeoutMS=5000,
        )

        # Test connection
        await _mongodb_client.admin.command("ping")

        _mongodb_database = _mongodb_client[settings.mongodb_db_name]

        # Create indexes
        await _create_indexes()

        logger.info(
            "mongodb_initialized",
            database=settings.mongodb_db_name,
            collections=await _mongodb_database.list_collection_names(),
        )

    except Exception as e:
        logger.error("mongodb_initialization_failed", error=str(e))
        raise


async def close_db() -> None:
    """Close MongoDB connection."""
    global _mongodb_client

    if _mongodb_client:
        _mongodb_client.close()
        logger.info("mongodb_connection_closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance.

    Returns:
        MongoDB database instance

    Raises:
        RuntimeError: If database is not initialized
    """
    if _mongodb_database is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _mongodb_database


def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """Get a MongoDB collection.

    Args:
        collection_name: Name of the collection

    Returns:
        MongoDB collection instance
    """
    db = get_database()
    return db[collection_name]


async def _create_indexes() -> None:
    """Create database indexes for optimal performance."""
    db = get_database()

    # Users collection indexes
    users_collection = db["users"]
    await users_collection.create_index("userId", unique=True)
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("profile.department")
    await users_collection.create_index("profile.role")

    # Conversations collection indexes
    conversations_collection = db["conversations"]
    await conversations_collection.create_index("sessionId", unique=True)
    await conversations_collection.create_index("userId")
    await conversations_collection.create_index([("userId", 1), ("createdAt", -1)])
    await conversations_collection.create_index("cycleType")
    await conversations_collection.create_index("isComplete")

    # Documents collection indexes
    documents_collection = db["documents"]
    await documents_collection.create_index("documentId", unique=True)
    await documents_collection.create_index("department")
    await documents_collection.create_index("accessLevel")
    await documents_collection.create_index("tags")
    await documents_collection.create_index("topics")

    logger.info("database_indexes_created")


async def check_connection() -> bool:
    """Check if MongoDB connection is healthy.

    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        if _mongodb_client:
            await _mongodb_client.admin.command("ping")
            return True
        return False
    except Exception as e:
        logger.error("mongodb_health_check_failed", error=str(e))
        return False
