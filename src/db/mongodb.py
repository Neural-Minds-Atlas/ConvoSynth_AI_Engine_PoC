"""MongoDB connection and database management."""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.db.mongodb_ssl_fix import create_ssl_context

logger = get_logger(__name__)
settings = get_settings()

# Global MongoDB client
_mongodb_client: Optional[AsyncIOMotorClient] = None
_mongodb_database: Optional[AsyncIOMotorDatabase] = None


async def init_db() -> None:
    """Initialize MongoDB connection.

    Validates connection and ensures we can connect to the specified database
    before allowing any operations. Will not create new databases automatically.

    Raises:
        ConnectionError: If cannot connect to MongoDB server
        RuntimeError: If specified database doesn't exist or cannot be accessed
    """
    global _mongodb_client, _mongodb_database

    try:
        logger.info(
            "initializing_mongodb",
            uri=settings.mongodb_uri,
            database=settings.mongodb_db_name,
        )

        # Import certifi for proper SSL certificates
        import certifi

        # Step 1: Create MongoDB client
        _mongodb_client = AsyncIOMotorClient(
            settings.mongodb_uri,
            minPoolSize=settings.mongodb_min_pool_size,
            maxPoolSize=settings.mongodb_max_pool_size,
            serverSelectionTimeoutMS=10000,
            tls=True,
            tlsCAFile=certifi.where(),
        )

        # Step 2: Test connection to MongoDB server
        logger.info("testing_mongodb_connection", uri=settings.mongodb_uri)
        try:
            await _mongodb_client.admin.command("ping")
            logger.info("mongodb_connection_successful")
        except Exception as conn_error:
            _mongodb_client = None
            _mongodb_database = None
            logger.error(
                "mongodb_connection_failed",
                error=str(conn_error),
                error_type=type(conn_error).__name__,
            )
            raise ConnectionError(
                f"❌ Cannot connect to MongoDB Atlas at {settings.mongodb_uri}\n"
                f"Error: {str(conn_error)}\n\n"
                f"Possible issues:\n"
                f"1. Network connectivity - Check your internet connection\n"
                f"2. SSL/TLS issue - On Windows, use Docker (see README_MONGODB_ATLAS.md)\n"
                f"3. IP not whitelisted - Add your IP at https://cloud.mongodb.com/ → Network Access\n"
                f"4. Wrong credentials - Check MONGODB_URI in .env\n"
                f"5. MongoDB Atlas down - Check status at https://status.mongodb.com/"
            ) from conn_error

        # Step 3: Check if the specified database exists
        logger.info("checking_database_exists", database=settings.mongodb_db_name)
        existing_databases = await _mongodb_client.list_database_names()

        if settings.mongodb_db_name not in existing_databases:
            # Database doesn't exist - we won't create it automatically
            logger.warning(
                "database_not_found",
                database=settings.mongodb_db_name,
                existing_databases=existing_databases,
            )
            # For now, we'll allow creating it if it doesn't exist
            # This is useful for first-time setup
            logger.info(
                "creating_new_database",
                database=settings.mongodb_db_name,
                note="Database will be created on first write operation",
            )
        else:
            logger.info(
                "database_found",
                database=settings.mongodb_db_name,
            )

        # Step 4: Get database reference
        _mongodb_database = _mongodb_client[settings.mongodb_db_name]

        # Step 5: Verify we can list collections (NO INDEX CREATION as per user request)
        collections = await _mongodb_database.list_collection_names()
        logger.info(
            "mongodb_initialized",
            database=settings.mongodb_db_name,
            collections=collections,
            collection_count=len(collections),
        )

    except ConnectionError:
        # Re-raise connection errors as-is
        raise
    except Exception as e:
        # Clean up on any other error
        _mongodb_client = None
        _mongodb_database = None
        logger.error(
            "mongodb_initialization_failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise RuntimeError(
            f"❌ Failed to initialize MongoDB database '{settings.mongodb_db_name}'\n"
            f"Error: {str(e)}\n\n"
            f"The MongoDB server is reachable, but there was an issue initializing the database.\n"
            f"Check your database permissions and configuration."
        ) from e


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


# NOTE: Index creation removed as per user request
# Indexes should be managed directly in MongoDB Atlas console if needed
# async def _create_indexes() -> None:
#     """Create database indexes for optimal performance."""
#     pass


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
