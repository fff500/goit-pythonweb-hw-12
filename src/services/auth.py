from datetime import datetime, timedelta, UTC
from typing import Optional, Literal
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.models import User
from src.services.users import UserService
from src.database.db import get_db
from src.conf.config import settings
from src.schemas import Token, UserModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ACCESS_TOKEN_EXPIRE_MINUTES = 15


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)


def create_token(
    data: dict, expires_delta: timedelta, token_type: Literal["access", "refresh"]
) -> Token:
    """
    Create a JWT token with the provided data and expiration time.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta): The time delta for token expiration.
        token_type (Literal["access", "refresh"]): The type of token being created.

    Returns:
        Token: The encoded JWT token.
    """

    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = now + expires_delta
    to_encode.update({"exp": expire, "iat": now, "token_type": token_type})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create a new access token for the user.

    Args:
        data (dict): The data to encode in the token, typically user information.
        expires_delta (Optional[float]): Optional expiration time in minutes. If not provided,

    Returns:
        Token: The encoded JWT token for access.
    """

    if expires_delta:
        access_token = create_token(data, expires_delta, "access")
    else:
        access_token = create_token(
            data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access"
        )
    return access_token


async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create a new refresh token for the user.

    Args:
        data (dict): The data to encode in the token, typically user information.
        expires_delta (Optional[float]): Optional expiration time in minutes. If not provided,
            defaults to REFRESH_TOKEN_EXPIRE_MINUTES.

    Returns:
        Token: The encoded JWT token for refresh.
    """

    if expires_delta:
        refresh_token = create_token(data, expires_delta, "refresh")
    else:
        refresh_token = create_token(
            data, timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES), "refresh"
        )
    return refresh_token


async def verify_refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Verify the provided refresh token and return the associated user if valid.

    Args:
        refresh_token (str): The refresh token to verify.
        db (AsyncSession): The database session dependency.

    Returns:
        User | None: The user associated with the refresh token if valid, otherwise None.
    """

    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        token_type: str = payload.get("token_type")
        if username is None or token_type != "refresh":
            return None
        query = select(User).filter_by(username=username, refresh_token=refresh_token)
        user = await db.execute(query)
        return user.scalar_one_or_none()
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserModel:
    """
    Get the current user based on the provided JWT token.

    Args:
        token (str): The JWT token provided by the user.
        db (AsyncSession): The database session dependency.

    Returns:
        UserModel: The user model of the currently authenticated user.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


async def get_email_from_token(token: str) -> str:
    """
    Get the email from the JWT token.

    Args:
        token (str): The JWT token containing the email.

    Returns:
        str: The email extracted from the token.
    """

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email verification token",
        )


def create_email_token(data: dict) -> Token:
    """
    Create an email verification token.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        Token: The encoded JWT token for email verification.
    """

    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    Gets the current authenticated admin user.

    Args:
        current_user (User): The currently authenticated user.

    Returns:
        User: The authenticated admin user.

    Raises:
        HTTPException: If the user does not have admin privileges.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient access rights")
    return current_user
