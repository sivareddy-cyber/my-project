from fastapi import APIRouter, HTTPException

try:
    from ..models.schemas import ReviewRequest, ReviewResponse
    from ..services.hindsight_service import hindsight_service
    from ..services.llm_service import llm_service
except (ImportError, ValueError):
    from models.schemas import ReviewRequest, ReviewResponse
    from services.hindsight_service import hindsight_service
    from services.llm_service import llm_service

router = APIRouter(tags=["Review"])


@router.post("/review", response_model=ReviewResponse)
async def review_code_endpoint(request: ReviewRequest) -> ReviewResponse:
    """
    Performs a team-aware code review:
    1. Recalls relevant team memories from Hindsight.
    2. Sends the code and recalled memories to Groq.
    3. Returns structured findings, suggestions, and memories used.
    """
    try:
        # Step 1: Recall relevant team rules/memories from Hindsight
        search_query = f"Rules, conventions, and disallowed patterns for {request.language} code:\n{request.code}"
        recalled_memories = await hindsight_service.recall_memories(query=search_query, limit=5)

        # Step 2: Generate review with Groq conditioned on recalled memories
        review_result = await llm_service.review_code(
            code=request.code,
            language=request.language,
            memories=recalled_memories,
        )

        return review_result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code review failed: {str(e)}"
        )
