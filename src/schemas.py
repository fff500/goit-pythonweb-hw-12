from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date
from typing import Optional


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birth_date: date
    description: Optional[str] = None


class ContactResponse(ContactModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    id: int
    email: EmailStr
    username: str

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
