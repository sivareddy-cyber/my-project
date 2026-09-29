"""
LLM Service Implementation (Phase 2)

Integrates with the official Groq API for ultra-fast, team-aware code reviews.
Injects recalled Hindsight memories directly into the LLM system prompt.
"""

import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from groq import Groq
try:
    from ..models.schemas import ReviewResponse, ReviewIssue
except (ImportError, ValueError):
    from models.schemas import ReviewResponse, ReviewIssue

load_dotenv()


class LLMService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self._client: Optional[Groq] = None

    def get_client(self) -> Optional[Groq]:
        """Lazily initialize and return the Groq client if API key is present."""
        if self._client is None:
            api_key_env = self.api_key or os.getenv("GROQ_API_KEY")
            if api_key_env:
                self._client = Groq(api_key=api_key_env)
        return self._client

    async def review_code(
        self,
        code: str,
        language: str,
        memories: Optional[List[str]] = None,
    ) -> ReviewResponse:
        """
        Performs a team-aware code review using Groq LLM, conditioned on recalled Hindsight memories.
        Falls back gracefully to a local rule checker if GROQ_API_KEY is not configured.
        """
        client = self.get_client()
        memories = memories or []

        if client:
            try:
                system_prompt = (
                    "You are an expert AI Code Reviewer for a software engineering team.\n"
                    "Your job is to review the submitted code and provide structured, actionable feedback.\n\n"
                    "CRITICAL INSTRUCTION - TEAM MEMORY ENFORCEMENT:\n"
                    "You have access to persistent team memories recalled from the team's Hindsight memory bank.\n"
                    "If the code violates any recalled team rule or standard, you MUST explicitly flag it as a team standard violation.\n\n"
                    "Output MUST be strict valid JSON matching this schema:\n"
                    "{\n"
                    '  "summary": "Brief summary of code quality and team convention adherence",\n'
                    '  "issues": [\n'
                    "    {\n"
                    '      "line": <line_number_or_null>,\n'
                    '      "severity": "info" | "warning" | "error",\n'
                    '      "description": "Clear explanation of the issue (note if it violates team memory)",\n'
                    '      "suggestion": "Recommended fix or replacement code"\n'
                    "    }\n"
                    "  ],\n"
                    '  "memories_used": ["Exact list of recalled team rules that were relevant to this review"]\n'
                    "}"
                )

                user_content = f"### PROGRAMMING LANGUAGE\n{language}\n\n"
                if memories:
                    user_content += "### RECALLED TEAM MEMORIES (from Hindsight):\n"
                    for i, mem in enumerate(memories, 1):
                        user_content += f"{i}. {mem}\n"
                    user_content += "\n"
                else:
                    user_content += "### RECALLED TEAM MEMORIES:\nNo specific team memories found for this context.\n\n"

                user_content += f"### CODE TO REVIEW:\n```\n{code}\n```"

                chat_completion = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )

                raw_response = chat_completion.choices[0].message.content
                data = json.loads(raw_response)

                issues = []
                for raw_issue in data.get("issues", []):
                    issues.append(
                        ReviewIssue(
                            line=raw_issue.get("line"),
                            severity=raw_issue.get("severity", "warning"),
                            description=raw_issue.get("description", ""),
                            suggestion=raw_issue.get("suggestion"),
                        )
                    )

                return ReviewResponse(
                    summary=data.get("summary", "Code review completed via Groq."),
                    issues=issues,
                    memories_used=data.get("memories_used", memories if memories else []),
                )
            except Exception as e:
                print(f"[LLMService] Groq review failed, falling back to local review engine: {e}")

        # Local Offline / Demo Review Fallback Engine
        issues = []
        lines = code.splitlines()

        # Check against recalled memories first
        memories_applied = []
        for mem in memories:
            mem_lower = mem.lower()
            if "console.log" in mem_lower or "console" in mem_lower or "disallow" in mem_lower or "log" in mem_lower:
                for idx, line in enumerate(lines, 1):
                    if "console.log" in line:
                        memories_applied.append(mem)
                        issues.append(
                            ReviewIssue(
                                line=idx,
                                severity="error",
                                description=f"Team Memory Violation: {mem}",
                                suggestion="// Replace console.log with structured logger (e.g. logger.info(...))",
                            )
                        )
            elif "timestamp" in mem_lower or "date.now" in mem_lower or "iso" in mem_lower:
                for idx, line in enumerate(lines, 1):
                    if "Date.now()" in line:
                        memories_applied.append(mem)
                        issues.append(
                            ReviewIssue(
                                line=idx,
                                severity="warning",
                                description=f"Team Convention: {mem}",
                                suggestion="timestamp: new Date().toISOString()",
                            )
                        )

        # General static checks
        for idx, line in enumerate(lines, 1):
            if "console.log" in line and not any(i.line == idx for i in issues):
                issues.append(
                    ReviewIssue(
                        line=idx,
                        severity="warning",
                        description="Direct console.log statement found in production code.",
                        suggestion="// Use standard logging utility",
                    )
                )
            if "TODO" in line or "FIXME" in line:
                issues.append(
                    ReviewIssue(
                        line=idx,
                        severity="info",
                        description="Unresolved TODO/FIXME comment.",
                        suggestion=None,
                    )
                )

        if not issues:
            summary = "Code looks clean! No team memory violations or lint issues detected (Local Engine)."
        else:
            summary = f"Identified {len(issues)} issue(s) matching team conventions and standards (Local Demo Mode)."

        return ReviewResponse(
            summary=summary,
            issues=issues,
            memories_used=list(set(memories_applied if memories_applied else memories)),
        )

    async def extract_learnings_from_feedback(
        self,
        feedback: str,
        review_context: Optional[str] = None,
    ) -> str:
        """
        Uses Groq (or fallback) to distill developer feedback into a concise, actionable team rule.
        """
        client = self.get_client()
        if client:
            try:
                prompt = (
                    "You are a knowledge extraction assistant for software teams.\n"
                    "Analyze the developer's feedback and extract a clear, standalone team rule or coding standard.\n"
                    "Output ONLY the concise rule statement (1-2 sentences), without quotes or preamble.\n\n"
                    f"Developer Feedback: {feedback}"
                )
                if review_context:
                    prompt += f"\nReview Context: {review_context}"

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass

        return feedback.strip()


llm_service = LLMService()
