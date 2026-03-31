from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from app.agent.state import SessionState
from app.llm.base import LLMProvider, Message

logger = logging.getLogger(__name__)

REVIEW_PROMPT = """You are a review analyst evaluating a persuasive statement for cross-partisan appeal.

The statement is written by someone with a {stance} stance on {topic}, targeting {target_audience}.

Statement to review:
---
{draft}
---

Evaluate the statement and respond with a JSON object:
{{
    "polarization_score": <0-10, where 0 = not polarizing at all, 10 = extremely polarizing>,
    "clarity_score": <0-10, where 10 = perfectly clear>,
    "persuasiveness_score": <0-10, where 10 = maximally persuasive for the target audience>,
    "flagged_phrases": ["<phrases that could trigger defensiveness in the target audience>"],
    "suggestions": ["<specific improvement suggestions>"],
    "strengths": ["<what the statement does well>"]
}}

Be specific and constructive. Focus on how the TARGET AUDIENCE would receive this statement."""


@dataclass
class ReviewResult:
    polarization_score: float = 5.0
    clarity_score: float = 5.0
    persuasiveness_score: float = 5.0
    flagged_phrases: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)


class ReviewLayer:
    """Evaluates drafts for polarization, clarity, and persuasiveness."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def review(self, draft: str, state: SessionState) -> ReviewResult:
        """Run a full review of the current draft."""
        prompt = REVIEW_PROMPT.format(
            stance=state.profile.get("stance", "unknown"),
            topic=state.profile.get("topic", "unknown"),
            target_audience=state.profile.get("target_audience", "unknown"),
            draft=draft,
        )

        try:
            response = await self.llm.complete(
                messages=[Message(role="user", content=prompt)],
                temperature=0.2,
                max_tokens=1024,
            )
            data = json.loads(response.strip().strip("```json").strip("```"))
            return ReviewResult(
                polarization_score=float(data.get("polarization_score", 5)),
                clarity_score=float(data.get("clarity_score", 5)),
                persuasiveness_score=float(data.get("persuasiveness_score", 5)),
                flagged_phrases=data.get("flagged_phrases", []),
                suggestions=data.get("suggestions", []),
                strengths=data.get("strengths", []),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Review analysis failed: %s", e)
            return ReviewResult()
