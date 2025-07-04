from unittest.mock import Mock
import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal


user_data = {
    "username": "samurai",
    "email": "samurai@gmail.com",
    "password": "1234567",
}


def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "nick",
            "email": "nick@example.com",
            "password": "7654321",
        },
    )
    assert response.status_code == 201


def test_register(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data


def test_repeat_register(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "User already exists"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email is not confirmed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).filter_by(email=user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.is_confirmed = True
            await session.commit()

        response = client.post(
            "api/auth/login",
            data={
                "username": user_data.get("username"),
                "password": user_data.get("password"),
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        user_data["refresh_token"] = data.get("refresh_token")
        assert "access_token" in data
        assert "token_type" in data


@pytest.mark.asyncio
async def test_refresh_token(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).filter_by(email=user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        print(current_user)
        response = client.post(
            "api/auth/refresh_token",
            json={
                "refresh_token": current_user.refresh_token,
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid credentials"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid credentials"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data
