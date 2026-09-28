from fastapi import APIRouter, HTTPException
from typing import Dict, Any

try:
    from ..models.schemas import MemoryRequest
    from ..services.hindsight_service import hindsight_service
except (ImportError, ValueError):
    from models.schemas import MemoryRequest
    from services.hindsight_service import hindsight_service

router = APIRouter(tags=["Memory"])


@router.post("/memory")
async def retain_memory_endpoint(request: MemoryRequest) -> Dict[str, Any]:
    """
    Accepts a team rule or standard and stores it in real Hindsight memory.
    """
    try:
        result = await hindsight_service.retain_memory(
            content=request.content,
            metadata={"source": "api_direct_teach"}
        )
        return {
            "status": "success",
            "message": "Rule successfully retained in Hindsight memory.",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retain memory in Hindsight: {str(e)}"
        )
