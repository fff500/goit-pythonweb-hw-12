from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.sql.sqltypes import DateTime


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    birth_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(String(150), nullable=True)

    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
