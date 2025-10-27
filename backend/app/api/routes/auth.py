"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.repositories import UserRepository, ConversationRepository
from app.db.models import UserDocument, UserProfile, ConversationDocument, ExtractedInformation, RBACValidation
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.api.dependencies import get_user_repository, get_conversation_repository, get_current_active_user
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_user_id,
    generate_session_id,
)
from app.utils.logger import get_logger
from app.utils.exceptions import AuthenticationException, ValidationException

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository),
):
    """Register a new user.

    Args:
        user_data: User registration data
        user_repo: User repository
        conversation_repo: Conversation repository

    Returns:
        JWT token, user info, and auto-created session ID

    Raises:
        HTTPException: If email already exists
    """
    # Check if user exists
    if await user_repo.user_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user_id = generate_user_id()
    password_hash = get_password_hash(user_data.password)

    profile = UserProfile(
        name=user_data.name,
        role=user_data.role,
        department=user_data.department,
        accessScopes=user_data.accessScopes,
        permissions=user_data.permissions,
    )

    user = UserDocument(
        userId=user_id,
        email=user_data.email,
        passwordHash=password_hash,
        profile=profile,
    )

    await user_repo.create_user(user)

    # Create access token
    access_token = create_access_token(data={"sub": user_id, "email": user.email})

    # Auto-create conversation session
    session_id = generate_session_id()
    conversation = ConversationDocument(
        sessionId=session_id,
        userId=user_id,
        cycleType="generation",
        messages=[],
        extractedInfo=ExtractedInformation(),
        rbacValidation=RBACValidation(),
    )
    await conversation_repo.create_conversation(conversation)

    logger.info("user_registered", user_id=user_id, email=user.email, session_id=session_id)

    return Token(
        accessToken=access_token,
        sessionId=session_id,
        user=UserResponse(
            userId=user.userId,
            email=user.email,
            profile=user.profile,
            isActive=user.isActive,
        ),
    )


@router.post("/login")
async def login(
    credentials: UserLogin,
    user_repo: UserRepository = Depends(get_user_repository),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository),
):
    """Login user.

    Args:
        credentials: Login credentials
        user_repo: User repository
        conversation_repo: Conversation repository

    Returns:
        JWT token, user info, and auto-created session ID

    Raises:
        HTTPException: If authentication fails
    """
    # Get user by email
    user = await user_repo.get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(credentials.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if active
    if not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.userId, "email": user.email})

    # Auto-create conversation session
    session_id = generate_session_id()
    conversation = ConversationDocument(
        sessionId=session_id,
        userId=user.userId,
        cycleType="generation",
        messages=[],
        extractedInfo=ExtractedInformation(),
        rbacValidation=RBACValidation(),
    )
    await conversation_repo.create_conversation(conversation)

    logger.info("user_logged_in", user_id=user.userId, email=user.email, session_id=session_id)

    # Return token with auto-generated session ID
    return {
        "accessToken": access_token,
        "tokenType": "bearer",
        "sessionId": session_id,
        "user": {
            "userId": user.userId,
            "email": user.email,
            "profile": {
                "name": user.profile.name,
                "role": user.profile.role,
                "department": user.profile.department,
                "accessScopes": user.profile.accessScopes,
                "permissions": user.profile.permissions.model_dump(),
            },
            "isActive": user.isActive,
        },
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserDocument = Depends(get_current_active_user),
):
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return UserResponse(
        userId=current_user.userId,
        email=current_user.email,
        profile=current_user.profile,
        isActive=current_user.isActive,
    )
