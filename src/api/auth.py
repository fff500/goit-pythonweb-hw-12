from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.services.email import send_email
from src.services.auth import (
    Hash,
    create_access_token,
    create_refresh_token,
    get_current_admin_user,
    get_email_from_token,
    verify_refresh_token,
)
from src.schemas import RequestEmail, Token, TokenRefreshRequest, UserCreate, UserModel
from src.services.users import UserService
from src.database.db import get_db


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    """
    Register a new user.

    Args:
        user_data (UserCreate): The data for the new user.
        background_tasks (BackgroundTasks): Background tasks to run after the response.
        request (Request): The request object to get the base URL for email confirmation.
        db (AsyncSession): The database session dependency.

    Returns:
        User: The newly created user.
    """

    user_service = UserService(db)

    user_by_email = await user_service.get_user_by_email(user_data.email)
    user_by_username = await user_service.get_user_by_username(user_data.username)
    if user_by_username or user_by_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Log in a user and return an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.
        db (AsyncSession): The database session dependency.

    Returns:
        Token: The access token for the authenticated user.
    """

    user_service = UserService(db)

    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not confirmed",
        )

    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})
    user.refresh_token = refresh_token
    await db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token", response_model=Token)
async def new_token(
    request: TokenRefreshRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Refresh the access token using a valid refresh token.

    Args:
        request (TokenRefreshRequest): The request body containing the refresh token.
        db (AsyncSession): The database session dependency.

    Returns:
        dict: A dictionary containing the new access token and the same refresh token.
    """

    user = await verify_refresh_token(request.refresh_token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    new_access_token = await create_access_token(data={"sub": user.username})
    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirm_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)) -> dict:
    """
    Confirm a user's email using a token.

    Args:
        token (str): The token sent to the user's email for confirmation.
        db (AsyncSession): The database session dependency.

    Returns:
        dict: A message indicating the result of the email confirmation.
    """

    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.is_confirmed:
        return {"message": "Email already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Request email confirmation for a user.

    Args:
        body (RequestEmail): The request body containing the user's email.
        background_tasks (BackgroundTasks): Background tasks to run after the response.
        request (Request): The request object to get the base URL for email confirmation.
        db (AsyncSession): The database session dependency.

    Returns:
        dict: A message indicating the result of the email request.
    """

    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.is_confirmed:
        return {"message": "Email already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation link"}


@router.get("/public")
def read_public():
    return {"message": "This is a public route accessible to everyone"}


@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    return {"message": f"Hello, {current_user.username}! This is an admin route."}
