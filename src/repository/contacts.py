"""
Contacts Repository Module
This module provides a repository for managing contact-related database operations.
"""

from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel


class ContactsRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the ContactsRepository.

        Args:
            session (AsyncSession): An asynchronous database session.
        """
        self.db = session

    async def get_contacts(self, user: User, skip: int, limit: int) -> List[Contact]:
        """
        Retrieve a list of contacts for the specified user with pagination.

        Args:
            user (User): The user for whom to retrieve contacts.
            skip (int): Number of contacts to skip for pagination.
            limit (int): Maximum number of contacts to return.

        Returns:
            List[Contact]: A list of contacts for the user.
        """

        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, user: User, contact_id: int) -> Contact | None:
        """
        Retrieve a specific contact by ID for the specified user.

        Args:
            user (User): The user for whom to retrieve the contact.
            contact_id (int): The ID of the contact to retrieve.

        Returns:
            Contact | None: The contact with the specified ID, or None if not found.
        """

        stmt = select(Contact).filter_by(user=user, id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def search_contacts(self, user: User, query: str) -> List[Contact]:
        """
        Search for contacts by first name, last name, or email for the specified user.

        Args:
            user (User): The user for whom to search contacts.
            query (str): The search query to match against first name, last name, or email.

        Returns:
            List[Contact]: A list of contacts matching the search query.
        """

        stmt = (
            select(Contact)
            .filter_by(user=user)
            .filter(
                (Contact.first_name.ilike(f"%{query}%"))
                | (Contact.last_name.ilike(f"%{query}%"))
                | (Contact.email.ilike(f"%{query}%"))
            )
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_birthdays_next_week(self, user: User) -> List[Contact]:
        """
        Retrieve contacts with birthdays in the next week for the specified user.

        Args:
            user (User): The user for whom to retrieve contacts with upcoming birthdays.

        Returns:
            List[Contact]: A list of contacts with birthdays in the next week.
        """

        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        stmt = (
            select(Contact)
            .filter_by(user=user)
            .filter(Contact.birth_date.between(today, next_week))
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def create_contact(self, user: User, body: ContactModel) -> Contact:
        """
        Create a new contact for the specified user.

        Args:
            user (User): The user for whom to create the contact.
            body (ContactModel): The contact data to create.

        Returns:
            Contact: The newly created contact.
        """

        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, user: User, contact_id: int, body: ContactModel
    ) -> Contact | None:
        """
        Update an existing contact for the specified user.

        Args:
            user (User): The user for whom to update the contact.
            contact_id (int): The ID of the contact to update.
            body (ContactModel): The updated contact data.

        Returns:
            Contact | None: The updated contact, or None if not found.
        """

        contact = await self.get_contact_by_id(user, contact_id)
        if contact:
            contact.first_name = body.first_name
            contact.last_name = body.last_name
            contact.email = body.email
            contact.phone = body.phone
            contact.birth_date = body.birth_date
            contact.description = body.description
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, user: User, contact_id: int) -> Contact | None:
        """
        Remove a contact for the specified user.

        Args:
            user (User): The user for whom to remove the contact.
            contact_id (int): The ID of the contact to remove.

        Returns:
            Contact | None: The removed contact, or None if not found.
        """

        contact = await self.get_contact_by_id(user, contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact
