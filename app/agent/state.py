from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.db.user import get_user_party
from app.db.conversation import get_conversation


class Stage(str, Enum):
    STAGE_1 = "stage_1"
    STAGE_2 = "stage_2"
    STAGE_3 = "stage_3"
    STAGE_4 = "stage_4"
    COMPLETE = "complete"


@dataclass
class SessionState:
    study_id: str
    stage: Stage = Stage.STAGE_1
    strategy: str = "common_identity"  # fixed for the session
    political_party: str | None = None  # "republican" or "democrat", set during intake
    stage_turn_count: int = 0  # turns within the current stage (resets on transition)
    # Condition-specific signals extracted by OBSERVE step
    signals: dict = field(default_factory=dict)
    memory: list[dict] = field(default_factory=list)
    turn_count: int = 0
    metadata: dict = field(default_factory=dict)


def build_session_state(
    study_id: str, strategy: str, messages: list[dict]
) -> SessionState:
    """Reconstruct SessionState from DB payload and current messages."""
    conversation = get_conversation(study_id)
    user_party = get_user_party(study_id)
    political_party = user_party.party if user_party is not None else None

    state = SessionState(
        study_id=study_id, strategy=strategy, political_party=political_party
    )

    # Populate from latest DB entry
    if conversation and conversation.get("payload"):
        payload = conversation["payload"]
        raw_stage = payload.get("stage", "stage_1")
        state.stage = Stage(raw_stage)
        state.political_party = political_party
        if political_party:
            state.signals["political_party"] = political_party
        # system_prompt is also in payload if needed
        state.metadata["last_observation"] = payload.get("last_observation", {})

    # Count turns from messages
    state.turn_count = sum(1 for m in messages if m.get("role") == "user")

    return state
