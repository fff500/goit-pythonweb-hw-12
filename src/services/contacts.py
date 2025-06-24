from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactsRepository
from src.schemas import ContactModel


class ContactsService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactsRepository(db)

    async def create_contact(self, user: User, body: ContactModel) -> Contact:
        return await self.repository.create_contact(user, body)

    async def get_contacts(
        self, user: User, skip: int, limit: int
    ) -> Sequence[Contact]:
        return await self.repository.get_contacts(user, skip, limit)

    async def get_contact(self, user: User, contact_id: int) -> Contact | None:
        return await self.repository.get_contact_by_id(user, contact_id)

    async def search_contacts(self, user: User, query: str) -> Sequence[Contact]:
        return await self.repository.search_contacts(user, query)

    async def get_birthdays_next_week(self, user: User) -> Sequence[Contact]:
        return await self.repository.get_birthdays_next_week(user)

    async def update_contact(
        self, user: User, contact_id: int, body: ContactModel
    ) -> Contact | None:
        return await self.repository.update_contact(user, contact_id, body)

    async def remove_contact(self, user: User, contact_id: int) -> Contact | None:
        return await self.repository.remove_contact(user, contact_id)
