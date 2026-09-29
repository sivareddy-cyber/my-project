from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="ok", description="Service health status")


class ReviewRequest(BaseModel):
    """Request schema for code review."""
    code: str = Field(..., min_length=1, description="Code snippet or diff to review")
    language: str = Field(default="javascript", description="Programming language of the code")


class MemoryRequest(BaseModel):
    """Request schema for manually retaining a team memory."""
    content: str = Field(..., min_length=1, description="Team rule, preference, or coding standard content")


class FeedbackRequest(BaseModel):
    """Request schema for developer feedback on a review."""
    review_id: Optional[str] = Field(default=None, description="Optional identifier of the reviewed submission")
    feedback: str = Field(..., min_length=1, description="Developer feedback text on the review accuracy/relevance")
    was_helpful: Optional[bool] = Field(default=None, description="Flag indicating if the review recommendations were helpful")
    corrections: Optional[str] = Field(default=None, description="Specific corrections or team rules clarified by the developer")


class ReviewIssue(BaseModel):
    """Individual issue or recommendation identified during code review."""
    line: Optional[int] = Field(default=None, description="Line number where issue was detected")
    severity: str = Field(default="warning", description="Severity level: info, warning, error")
    description: str = Field(..., description="Explanation of the issue or team standard violation")
    suggestion: Optional[str] = Field(default=None, description="Recommended code fix or improvement")


class ReviewResponse(BaseModel):
    """Response schema containing the complete code review results."""
    summary: str = Field(..., description="High-level overview of the review findings")
    issues: List[ReviewIssue] = Field(default_factory=list, description="List of detected issues and suggestions")
    memories_used: List[str] = Field(default_factory=list, description="List of team memories recalled and applied during the review")
