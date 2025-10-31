"""Conversation routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.db.models import UserDocument
from src.schemas.conversation import (
    ConversationRequest,
    ConversationResponse,
    ConversationHistoryResponse,
    SessionInfoResponse,
    SessionResetRequest,
)
from src.services import ConversationService
from src.api.dependencies_mongodb import get_current_active_user, get_conversation_service
from src.utils.logger import get_logger
from src.utils.exceptions import NotFoundException, AgentException

router = APIRouter(prefix="/conversation", tags=["Conversation"])
logger = get_logger(__name__)


@router.post("/generate", response_model=ConversationResponse)
async def conversation_generate(
    request: ConversationRequest,
    current_user: UserDocument = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Process conversation for new presentation generation.

    Args:
        request: Conversation request
        current_user: Current authenticated user
        conversation_service: Conversation service

    Returns:
        Conversation response with agent output

    Raises:
        HTTPException: If processing fails
    """
    try:
        # Force generation mode
        request.cycleType = "generation"
        request.editingContext = None

        result = await conversation_service.process_conversation(
            user_id=current_user.userId,
            request=request,
        )

        logger.info(
            "conversation_generated",
            user_id=current_user.userId,
            session_id=result.get("sessionId"),
            is_complete=result.get("isComplete"),
        )

        return ConversationResponse(**result)

    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AgentException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error("conversation_generation_failed", error=str(e), user_id=current_user.userId)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversation processing failed: {str(e)}",
        )


@router.post("/edit", response_model=ConversationResponse)
async def conversation_edit(
    request: ConversationRequest,
    current_user: UserDocument = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Process conversation for editing existing presentation.

    Args:
        request: Conversation request with editing context
        current_user: Current authenticated user
        conversation_service: Conversation service

    Returns:
        Conversation response with agent output

    Raises:
        HTTPException: If processing fails or editing context missing
    """
    try:
        # Force editing mode
        request.cycleType = "editing"

        if not request.editingContext:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Editing context is required for edit mode",
            )

        result = await conversation_service.process_conversation(
            user_id=current_user.userId,
            request=request,
        )

        logger.info(
            "conversation_edited",
            user_id=current_user.userId,
            session_id=result.get("sessionId"),
            is_complete=result.get("isComplete"),
        )

        return ConversationResponse(**result)

    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AgentException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error("conversation_edit_failed", error=str(e), user_id=current_user.userId)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversation editing failed: {str(e)}",
        )


@router.get("/session/{session_id}", response_model=SessionInfoResponse)
async def get_session(
    session_id: str,
    current_user: UserDocument = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Get session information.

    Args:
        session_id: Session ID
        current_user: Current authenticated user
        conversation_service: Conversation service

    Returns:
        Session information

    Raises:
        HTTPException: If session not found
    """
    try:
        conversation = await conversation_service.get_session_info(session_id)

        if not conversation:
            raise NotFoundException("Session", session_id)

        # Verify user owns this session
        if conversation.userId != current_user.userId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this session",
            )

        return SessionInfoResponse(
            sessionId=conversation.sessionId,
            userId=conversation.userId,
            cycleType=conversation.cycleType,
            messageCount=len(conversation.messages),
            isComplete=conversation.extractedInfo.isComplete,
            confidenceScore=conversation.extractedInfo.confidenceScore,
            conversationState=conversation.extractedInfo.conversationState,
            createdAt=conversation.createdAt,
            updatedAt=conversation.updatedAt,
        )

    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")


@router.post("/session/reset")
async def reset_session(
    request: SessionResetRequest,
    current_user: UserDocument = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Reset a conversation session.

    Args:
        request: Session reset request
        current_user: Current authenticated user
        conversation_service: Conversation service

    Returns:
        Success message

    Raises:
        HTTPException: If session not found or unauthorized
    """
    try:
        conversation = await conversation_service.get_session_info(request.sessionId)

        if not conversation:
            raise NotFoundException("Session", request.sessionId)

        # Verify user owns this session
        if conversation.userId != current_user.userId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to reset this session",
            )

        await conversation_service.reset_session(request.sessionId)

        logger.info("session_reset", session_id=request.sessionId, user_id=current_user.userId)

        return {"message": "Session reset successfully", "sessionId": request.sessionId}

    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {request.sessionId} not found")


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: UserDocument = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Delete a conversation session.

    Args:
        session_id: Session ID
        current_user: Current authenticated user
        conversation_service: Conversation service

    Returns:
        Success message

    Raises:
        HTTPException: If session not found or unauthorized
    """
    try:
        conversation = await conversation_service.get_session_info(session_id)

        if not conversation:
            raise NotFoundException("Session", session_id)

        # Verify user owns this session
        if conversation.userId != current_user.userId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this session",
            )

        deleted = await conversation_service.delete_session(session_id)

        if deleted:
            logger.info("session_deleted", session_id=session_id, user_id=current_user.userId)
            return {"message": "Session deleted successfully", "sessionId": session_id}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")


@router.get("/history", response_model=ConversationHistoryResponse)
async def get_user_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cycle_type: Optional[str] = Query(None, description="Filter by cycle type"),
    current_user: UserDocument = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Get user's conversation history.

    Args:
        page: Page number
        page_size: Items per page
        cycle_type: Optional filter by cycle type
        current_user: Current authenticated user
        conversation_service: Conversation service

    Returns:
        Conversation history
    """
    skip = (page - 1) * page_size

    history = await conversation_service.get_user_conversations(
        user_id=current_user.userId,
        skip=skip,
        limit=page_size,
        cycle_type=cycle_type,
    )

    return ConversationHistoryResponse(**history)
