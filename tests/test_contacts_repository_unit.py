from datetime import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactsRepository
from src.schemas import ContactModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactsRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(first_name="Paul", user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    # Assertions
    assert len(contacts) == 1
    for contact in contacts:
        assert contact.user.id == 1
        assert contact.first_name == "Paul"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, first_name="Paul", user=user
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "Paul"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactModel(
        email="foo@bar.com",
        first_name="Paul",
        last_name="Smith",
        phone="222-222-2222",
        birth_date=datetime(day=5, month=7, year=1990),
    )

    # Call method
    created_contact = await contact_repository.create_contact(user, contact_data)

    # Assertions
    assert created_contact is not None
    assert isinstance(created_contact, Contact)
    assert created_contact.first_name == "Paul"
    assert created_contact.email == "foo@bar.com"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(created_contact)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactModel(
        first_name="Nick", last_name="Owens", email="foo@bar.com"
    )
    existing_contact = Contact(id=1, first_name="Paul", last_name="Smith", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(
        user=user, contact_id=1, body=contact_data
    )

    # Assertions
    assert result is not None
    assert result.first_name == "Nick"
    assert result.last_name == "Owens"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    # Setup
    existing_contact = Contact(id=1, first_name="Paul", last_name="Owens", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.last_name == "Owens"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
