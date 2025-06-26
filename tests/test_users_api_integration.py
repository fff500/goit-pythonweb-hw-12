import io
from unittest.mock import Mock, patch, AsyncMock
import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal, test_admin_user


user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "user",
}


def test_register(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data


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
    assert "access_token" in data
    assert "token_type" in data
    return data


@pytest.mark.asyncio
async def test_get_me(client):
    response = await test_login(client)
    token = response.get("access_token")
    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200 or response.status_code == 405


@pytest.mark.asyncio
async def test_update_avatar(client):
    token_object = await test_login(client)
    token = token_object.get("access_token")

    with patch(
        "src.api.users.UserService.update_avatar_url", new_callable=AsyncMock
    ) as mock_update_avatar:
        mock_update_avatar.return_value = test_admin_user
        with patch(
            "src.api.users.UploadFileService.upload_file", new_callable=Mock
        ) as mock_upload:
            mock_upload.return_value = "https://fake-avatar-url.com/avatar.png"

            fake_file = io.BytesIO(b"avatar image data")
            fake_file.name = "avatar.png"

            response = client.patch(
                "/api/users/avatar",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("avatar.png", fake_file, "image/png")},
            )
            assert response.status_code == 200
