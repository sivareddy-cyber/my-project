from fastapi import APIRouter

try:
    from ..models.schemas import HealthResponse
except (ImportError, ValueError):
    from models.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Returns the operational status of the backend API."""
    return HealthResponse(status="ok")
