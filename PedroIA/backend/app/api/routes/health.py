from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.llm_engine.router import get_router

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    status = get_router().status()
    return HealthResponse(
        status="ok",
        online=status["online"],
        cloud_providers=status["cloud_providers"],
        ollama=status["ollama"],
    )
