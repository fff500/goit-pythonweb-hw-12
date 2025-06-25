from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import date
from typing import Optional


class ContactModel(BaseModel):
    first_name: str
    last_name: Optional[str] = Field(default=None, max_length=30)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=12)
    birth_date: Optional[date] = Field(default=None)
    description: Optional[str] = None


class ContactResponse(ContactModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr


class TokenRefreshRequest(BaseModel):
    refresh_token: str
