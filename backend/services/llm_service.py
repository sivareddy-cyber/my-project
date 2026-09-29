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
from ..models.schemas import ReviewResponse, ReviewIssue

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

    def get_client(self) -> Groq:
        """Lazily initialize and return the Groq client."""
        if self._client is None:
            api_key_env = self.api_key or os.getenv("GROQ_API_KEY")
            if not api_key_env:
                raise ValueError("GROQ_API_KEY is not set in the environment or backend/.env file.")
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
        
        Args:
            code: Source code to review.
            language: Programming language.
            memories: Recalled team conventions and rules from Hindsight.
            
        Returns:
            Structured ReviewResponse.
        """
        client = self.get_client()
        memories = memories or []

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
            summary=data.get("summary", "Code review completed."),
            issues=issues,
            memories_used=data.get("memories_used", memories if memories else []),
        )

    async def extract_learnings_from_feedback(
        self,
        feedback: str,
        review_context: Optional[str] = None,
    ) -> str:
        """
        Uses Groq to distill developer feedback into a concise, actionable team rule for Hindsight.
        """
        client = self.get_client()
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


llm_service = LLMService()
