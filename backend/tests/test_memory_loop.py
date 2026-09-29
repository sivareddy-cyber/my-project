import sys
import os
from unittest.mock import patch, MagicMock

# Setup path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
for p in (backend_dir, root_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
try:
    from backend.main import app
    from backend.models.schemas import ReviewResponse, ReviewIssue
except ImportError:
    from main import app
    from models.schemas import ReviewResponse, ReviewIssue

client = TestClient(app)


def test_post_memory_endpoint():
    """Verify POST /memory successfully receives a rule and delegates to hindsight_service."""
    with patch("backend.services.hindsight_service.hindsight_service.retain_memory") as mock_retain:
        mock_retain.return_value = {
            "bank_id": "test-bank",
            "content": "Our team does not allow console.log() in production code.",
            "status": "retained",
        }

        response = client.post(
            "/memory",
            json={"content": "Our team does not allow console.log() in production code."},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "retained in Hindsight" in data["message"]


def test_post_review_endpoint_with_recalled_memory():
    """Verify POST /review recalls memories and forwards them to Groq LLM service."""
    with patch("backend.services.hindsight_service.hindsight_service.recall_memories") as mock_recall, \
         patch("backend.services.llm_service.llm_service.review_code") as mock_review:

        # Mock recall returning the team rule
        mock_recall.return_value = ["Our team does not allow console.log() in production code."]

        # Mock LLM review detecting the violation
        mock_review.return_value = ReviewResponse(
            summary="Code violates team logging conventions.",
            issues=[
                ReviewIssue(
                    line=2,
                    severity="error",
                    description="Detected console.log() which is disallowed by team standards.",
                    suggestion="Use structured logger instead.",
                )
            ],
            memories_used=["Our team does not allow console.log() in production code."],
        )

        response = client.post(
            "/review",
            json={
                "code": "function calculateTotal(items) {\n  console.log('Calculating total:', items);\n  return items.reduce((a, b) => a + b, 0);\n}",
                "language": "javascript",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "console.log" in data["summary"] or len(data["issues"]) > 0
        assert data["issues"][0]["severity"] == "error"
        assert "Our team does not allow console.log() in production code." in data["memories_used"]


def test_post_feedback_endpoint():
    """Verify POST /feedback retains developer feedback into Hindsight."""
    with patch("backend.services.hindsight_service.hindsight_service.retain_memory") as mock_retain:
        mock_retain.return_value = {
            "bank_id": "test-bank",
            "content": "Team feedback/standard: Avoid any usage of eval() in helper scripts",
            "status": "retained",
        }

        response = client.post(
            "/feedback",
            json={
                "review_id": "rev-123",
                "feedback": "Never use eval() in helper utilities.",
                "was_helpful": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
