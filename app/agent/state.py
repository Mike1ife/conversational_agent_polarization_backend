from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum


class Stage(str, Enum):
    INTAKE = "intake"
    STAGE_1 = "stage_1"
    STAGE_2 = "stage_2"
    STAGE_3 = "stage_3"
    STAGE_4 = "stage_4"
    COMPLETE = "complete"


@dataclass
class SessionState:
    session_id: str
    stage: Stage = Stage.INTAKE
    strategy: str = "common_identity"  # fixed for the session
    political_party: str | None = None  # "republican" or "democrat", set during intake
    stage_turn_count: int = 0  # turns within the current stage (resets on transition)
    # Condition-specific signals extracted by OBSERVE step
    signals: dict = field(default_factory=dict)
    memory: list[dict] = field(default_factory=list)
    turn_count: int = 0
    metadata: dict = field(default_factory=dict)


class StateManager:
    """In-memory session state store."""

    def __init__(self):
        self._sessions: dict[str, SessionState] = {}

    def _compute_session_id(self, messages: list[dict], strategy: str = "") -> str:
        """Derive a stable session ID from the first user message + strategy.

        Consistent across all turns since the first user message never changes.
        """
        for msg in messages:
            if msg.get("role") == "user":
                raw = f"{strategy}:{msg['content'][:200]}"
                return hashlib.sha256(raw.encode()).hexdigest()[:16]
        return hashlib.sha256(strategy.encode()).hexdigest()[:16]

    def get_or_create(
        self,
        messages: list[dict],
        strategy: str,
        session_id: str | None = None,
    ) -> SessionState:
        if session_id is None:
            session_id = self._compute_session_id(messages, strategy)

        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(
                session_id=session_id,
                strategy=strategy,
            )
        state = self._sessions[session_id]
        state.turn_count = sum(1 for m in messages if m.get("role") == "user")
        return state

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
