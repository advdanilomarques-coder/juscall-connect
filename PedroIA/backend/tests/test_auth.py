"""Auth flow tests: register -> login -> use token on chat."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_register_login_and_chat_with_jwt():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register
        r = await client.post(
            "/api/v1/auth/register",
            json={"email": "dev@example.com", "password": "secret123", "display_name": "Dev"},
        )
        assert r.status_code == 201, r.text
        token = r.json()["access_token"]
        assert token

        # Duplicate register fails
        r2 = await client.post(
            "/api/v1/auth/register", json={"email": "dev@example.com", "password": "secret123"}
        )
        assert r2.status_code == 409

        # Login
        r3 = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "secret123"}
        )
        assert r3.status_code == 200
        token = r3.json()["access_token"]

        # Wrong password
        r4 = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "nope"}
        )
        assert r4.status_code == 401

        # me
        r5 = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r5.status_code == 200
        assert r5.json()["email"] == "dev@example.com"

        # Chat works with the JWT (falls back to config provider message here)
        r6 = await client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "oi"}], "mode": "local"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r6.status_code == 200
        assert "content" in r6.json()


@pytest.mark.asyncio
async def test_invalid_email_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/v1/auth/register", json={"email": "bad", "password": "secret123"})
        assert r.status_code == 422
