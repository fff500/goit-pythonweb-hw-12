from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        return await self.repository.create_user(body)

    async def get_user_by_email(self, email: EmailStr):
        return await self.repository.get_user_by_email(email)

    async def get_user_by_username(self, username: str):
        return await self.repository.get_user_by_username(username)

    async def confirm_email(self, email: str):
        return await self.repository.confirm_email(email)

    async def update_avatar_url(self, email: str, url: str):
        return await self.repository.update_avatar_url(email, url)
