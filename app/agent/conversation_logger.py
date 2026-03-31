from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from app.agent.state import SessionState
from app.db.conversation import save_turn_log
from app.llm.base import Message

logger = logging.getLogger(__name__)


def log_turn(
    conversations_dir: str,
    state: SessionState,
    system_prompt: str,
    messages: list[Message],
    response: str,
) -> None:
    """Append a single conversation turn to the session's JSONL log file."""
    try:
        path = Path(conversations_dir)
        path.mkdir(parents=True, exist_ok=True)

        entry = {
            "session_id": state.session_id,
            "study_id": state.metadata.get("study_id"),
            "conversation_id": state.metadata.get("conversation_id"),
            "turn": state.turn_count,
            "stage": state.stage.value,
            "strategy": state.strategy,
            "political_party": state.political_party,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_prompt": system_prompt,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "response": response,
        }

        conversation_id = state.metadata.get("conversation_id")
        study_id = state.metadata.get("study_id")
        if conversation_id and study_id:
            save_turn_log(
                conversation_id=conversation_id,
                study_id=study_id,
                entry=entry,
            )

        log_file = path / f"{state.session_id}.jsonl"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    except Exception as e:
        logger.warning("Failed to log conversation turn: %s", e)
