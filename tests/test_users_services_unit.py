import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.users import UserService
from src.schemas import UserCreate
from src.database.models import User


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    return repo


@pytest.fixture
def user_service(mock_repository):
    service = UserService.__new__(UserService)
    service.repository = mock_repository
    return service


@pytest.mark.asyncio
async def test_create_user(user_service, mock_repository):
    user_data = UserCreate(
        username="testuser", email="test@example.com", password="secret"
    )

    mock_repository.create_user = AsyncMock(return_value=User(username="testuser"))

    result = await user_service.create_user(user_data)

    assert isinstance(result, User)
    assert result.username == "testuser"
    mock_repository.create_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_user_by_username(user_service, mock_repository):
    mock_repository.get_user_by_username = AsyncMock(
        return_value=User(username="testuser")
    )
    user = await user_service.get_user_by_username("testuser")

    assert user.username == "testuser"
    mock_repository.get_user_by_username.assert_awaited_once_with("testuser")


@pytest.mark.asyncio
async def test_get_user_by_email(user_service, mock_repository):
    email = "test@example.com"
    mock_repository.get_user_by_email = AsyncMock(return_value=User(email=email))
    user = await user_service.get_user_by_email(email)

    assert user.email == email
    mock_repository.get_user_by_email.assert_awaited_once_with(email)


@pytest.mark.asyncio
async def test_update_avatar_url(user_service, mock_repository):
    email = "test@example.com"
    url = "http://avatar.url"
    mock_repository.update_avatar_url = AsyncMock(
        return_value=User(email=email, avatar=url)
    )

    user = await user_service.update_avatar_url(email, url)

    assert user.avatar == url
    mock_repository.update_avatar_url.assert_awaited_once_with(email, url)
