from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.services.auth import get_current_user
from src.database.db import get_db
from src.schemas import ContactResponse, ContactModel
from src.services.contacts import ContactsService


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[ContactResponse]:
    """
    Retrieve a list of contacts for the authenticated user.

    Args:
        skip (int): Number of contacts to skip for pagination.
        limit (int): Maximum number of contacts to return.
        db (AsyncSession): The database session dependency.
        user (User): The authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts for the user.
    """

    contacts_service = ContactsService(db)
    contacts = await contacts_service.get_contacts(user, skip, limit)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ContactResponse:
    """
    Retrieve a specific contact by ID for the authenticated user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session dependency.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The contact with the specified ID.
    """

    contacts_service = ContactsService(db)
    contact = await contacts_service.get_contact(user, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/search/")
async def search_contacts(
    query: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[ContactResponse]:
    """
    Search for contacts by a query string.

    Args:
        query (str): The search query string.
        db (AsyncSession): The database session dependency.
        user (User): The authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts matching the search query.
    """

    contacts_service = ContactsService(db)
    contacts = await contacts_service.search_contacts(user, query)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_birthdays_next_week(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
) -> List[ContactResponse]:
    """
    List contacts with birthdays in the next week.

    Args:
        db (AsyncSession): The database session dependency.
        user (User): The authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts with birthdays in the next week.
    """
    contacts_service = ContactsService(db)
    contacts = await contacts_service.get_birthdays_next_week(user)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ContactResponse:
    """
    Create a new contact for the authenticated user.

    Args:
        body (ContactModel): The data for the new contact.
        db (AsyncSession): The database session dependency.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The newly created contact.
    """

    contacts_service = ContactsService(db)
    return await contacts_service.create_contact(user, body)


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ContactResponse:
    """
    Update an existing contact for the authenticated user.

    Args:
        body (ContactModel): The updated data for the contact.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The database session dependency.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The updated contact.
    """

    contacts_service = ContactsService(db)
    contact = await contacts_service.update_contact(user, contact_id, body)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ContactResponse:
    """
    Remove a contact for the authenticated user.

    Args:
        contact_id (int): The ID of the contact to remove.
        db (AsyncSession): The database session dependency.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The removed contact.
    """

    contacts_service = ContactsService(db)
    contact = await contacts_service.remove_contact(user, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
