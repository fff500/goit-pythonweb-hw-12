from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel


class ContactsRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, user: User, skip: int, limit: int) -> List[Contact]:
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, user: User, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(user=user, id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def search_contacts(self, user: User, query: str) -> List[Contact]:
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
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, user: User, contact_id: int, body: ContactModel
    ) -> Contact | None:
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
        contact = await self.get_contact_by_id(user, contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact
