"""Smoke tests that run with zero external dependencies (fallback provider)."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.llm_engine.prompts import build_system_prompt, detect_slash
from app.llm_engine.router import ModelRouter
from app.main import app


def test_detect_slash():
    assert detect_slash("/fix corrija isso") == "/fix"
    assert detect_slash("  /security ...") == "/security"
    assert detect_slash("olá") is None


def test_system_prompt_includes_slash_guidance():
    prompt = build_system_prompt("/test crie testes", "Arquivo: a.py")
    assert "PedroIA" in prompt
    assert "testes" in prompt.lower()
    assert "Arquivo: a.py" in prompt


def test_router_selects_fallback_without_config():
    router = ModelRouter()
    provider = router.select("local")
    # Without Ollama running, local mode degrades to fallback.
    assert provider.name in ("fallback", "ollama")


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "online" in body


@pytest.mark.asyncio
async def test_chat_endpoint_fallback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "olá"}], "mode": "local"},
        )
    assert resp.status_code == 200
    assert "content" in resp.json()
