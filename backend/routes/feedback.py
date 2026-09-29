from fastapi import APIRouter, HTTPException
from typing import Dict, Any

try:
    from ..models.schemas import FeedbackRequest
    from ..services.hindsight_service import hindsight_service
    from ..services.llm_service import llm_service
except (ImportError, ValueError):
    from models.schemas import FeedbackRequest
    from services.hindsight_service import hindsight_service
    from services.llm_service import llm_service

router = APIRouter(tags=["Feedback"])


@router.post("/feedback")
async def provide_feedback_endpoint(request: FeedbackRequest) -> Dict[str, Any]:
    """
    Stores developer feedback in Hindsight, distilling actionable rules if needed.
    """
    try:
        feedback_content = request.feedback
        if request.corrections:
            feedback_content += f"\nSpecific correction: {request.corrections}"

        # If LLM key is present, optionally distill into a concise rule
        distilled_rule = None
        try:
            distilled_rule = await llm_service.extract_learnings_from_feedback(
                feedback=feedback_content
            )
        except Exception:
            pass

        content_to_retain = distilled_rule or feedback_content

        result = await hindsight_service.retain_memory(
            content=f"Team feedback/standard: {content_to_retain}",
            metadata={
                "source": "developer_feedback",
                "review_id": str(request.review_id or "")
            }
        )

        return {
            "status": "success",
            "message": "Feedback successfully processed and retained in Hindsight.",
            "retained_rule": content_to_retain,
            "data": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record feedback in Hindsight: {str(e)}"
        )
