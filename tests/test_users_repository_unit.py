import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import UserCreate
from src.database.models import Contact, User
from src.repository.users import UsersRepository


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UsersRepository(mock_session)


@pytest.fixture
def contact():
    return Contact(id=1, email="sky@walker.com")


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="Paul")
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await user_repository.get_user_by_id(user_id=1)
    # Assertions
    assert user is not None
    assert user.id == 1
    assert user.username == "Paul"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="Bill")
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await user_repository.get_user_by_username(username="Bill")
    # Assertions
    assert user is not None
    assert user.id == 1
    assert user.username == "Bill"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, email="foo@bar.com")
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await user_repository.get_user_by_email(email="foo@bar.com")
    # Assertions
    assert user is not None
    assert user.id == 1
    assert user.email == "foo@bar.com"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="hashed_password",
    )

    # Call method
    created_user = await user_repository.create_user(user_data)

    # Assertions
    assert created_user is not None
    assert isinstance(created_user, User)
    assert created_user.username == "testuser"
    assert created_user.email == "test@example.com"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(created_user)
