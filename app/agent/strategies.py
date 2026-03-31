from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Strategy(str, Enum):
    COMMON_IDENTITY = "common_identity"
    PERSONAL_NARRATIVE = "personal_narrative"
    MISPERCEPTION_CORRECTION = "misperception_correction"


@dataclass
class StrategyConfig:
    """Configuration for a study condition."""

    name: Strategy
    description: str
    guidance_principles: list[str] = field(default_factory=list)


STRATEGY_CONFIGS: dict[Strategy, StrategyConfig] = {
    Strategy.COMMON_IDENTITY: StrategyConfig(
        name=Strategy.COMMON_IDENTITY,
        description=(
            "Guide the user — through questions and reflection — toward recognizing "
            "that media may distort their picture of the opposing party, and that most "
            "ordinary Americans share a common exhaustion with polarization."
        ),
    ),
    Strategy.PERSONAL_NARRATIVE: StrategyConfig(
        name=Strategy.PERSONAL_NARRATIVE,
        description=(
            "Help the user think carefully and concretely about a specific person they "
            "know who supports the opposing party — to see that person as a full, complex "
            "human being rather than as a representative of a political category."
        ),
    ),
    Strategy.MISPERCEPTION_CORRECTION: StrategyConfig(
        name=Strategy.MISPERCEPTION_CORRECTION,
        description=(
            "Correct the user's misperceptions about the opposing party's attitudes toward "
            "democracy by asking them to estimate what the other party believes about "
            "anti-democratic actions, then revealing accurate survey data showing that the "
            "other party overwhelmingly rejects those actions."
        ),
    ),
}


def get_strategy(name: str) -> StrategyConfig:
    """Get strategy configuration by name."""
    try:
        return STRATEGY_CONFIGS[Strategy(name.lower())]
    except (ValueError, KeyError):
        raise ValueError(
            f"Unknown condition '{name}'. Choose from: {', '.join(s.value for s in Strategy)}"
        )
