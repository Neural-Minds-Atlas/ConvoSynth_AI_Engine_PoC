"""FastAPI dependencies for dependency injection."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.db.repositories import (
    UserRepository,
    ConversationRepository,
    DocumentRepository,
)
from src.db.models import UserDocument
from src.services import RBACService, LLMService, ConversationService
from src.utils.security import decode_access_token
from src.utils.exceptions import AuthenticationException
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Security
security = HTTPBearer()


# Repositories
def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    return UserRepository()


def get_conversation_repository() -> ConversationRepository:
    """Get conversation repository instance."""
    return ConversationRepository()


def get_document_repository() -> DocumentRepository:
    """Get document repository instance."""
    return DocumentRepository()


# Services
def get_rbac_service() -> RBACService:
    """Get RBAC service instance."""
    return RBACService()


def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    return LLMService()


def get_conversation_service(
    user_repo: UserRepository = Depends(get_user_repository),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    rbac_service: RBACService = Depends(get_rbac_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> ConversationService:
    """Get conversation service instance."""
    return ConversationService(
        user_repo=user_repo,
        conversation_repo=conversation_repo,
        document_repo=document_repo,
        rbac_service=rbac_service,
        llm_service=llm_service,
    )


# Authentication
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserDocument:
    """Get current authenticated user.

    Args:
        credentials: JWT credentials from Authorization header
        user_repo: User repository

    Returns:
        Current user document

    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")

        user = await user_repo.get_user_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")

        if not user.isActive:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        logger.info("user_authenticated", user_id=user_id, email=user.email)
        return user

    except AuthenticationException as e:
        logger.warning("authentication_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("authentication_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: UserDocument = Depends(get_current_user),
) -> UserDocument:
    """Get current active user.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.isActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user
