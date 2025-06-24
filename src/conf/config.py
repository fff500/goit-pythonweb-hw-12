from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = (
        "postgresql+asyncpg://POSTGRES_USER:POSTGRES_PASSWORD@$POSTGRES_HOST:1234/POSTGRES_DB"
    )
    JWT_SECRET: str = "None"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr = "pavlo.tereshko@gmail.com"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM: EmailStr = "pavlo.tereshko@gmail.com"
    MAIL_PORT: int = 2
    MAIL_SERVER: str = "None"
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLOUDINARY_NAME: str = "None"
    CLOUDINARY_API_KEY: str = "None"
    CLOUDINARY_API_SECRET: str = "None"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
