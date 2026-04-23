from datetime import datetime, timezone

from app.schema import Message, MCObservation, ChatObservation
from app.db.documents import conversation_docs


def get_conversation(study_id: str) -> dict:
    return conversation_docs.find_one({"study_id": study_id})


def save_turn_log(study_id: str, entry: dict):
    now = datetime.now(timezone.utc)
    conversation_docs.update_one(
        {"study_id": study_id},
        {
            "$set": {
                "payload": entry,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )


def save_safety_event(study_id: str, verdict: dict):
    now = datetime.now(timezone.utc)
    conversation_docs.update_one(
        {"study_id": study_id},
        {
            "$set": {
                "verdict": verdict,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )


def _coerce_messages(messages: list | None) -> list[Message]:
    history: list[Message] = []

    for msg in messages or []:
        if not isinstance(msg, dict):
            continue

        role = msg.get("role")
        content = msg.get("content")
        if role in {"user", "assistant"} and isinstance(content, str):
            history.append(Message(role=role, content=content))

    return history


def get_chat_history(study_id: str) -> list:
    conversation_doc = conversation_docs.find_one({"study_id": study_id})

    if not conversation_doc:
        return []

    payload = conversation_doc.get("payload") or {}

    messages = payload.get("messages") or payload.get("message") or []
    return _coerce_messages(messages)


def _get_misperception_correction_observation(signals: dict) -> MCObservation:
    question_answers = signals.get("question_answers", {})
    return MCObservation(answers=list(question_answers.values()))


strategy_observation = {
    "misperception_correction": _get_misperception_correction_observation
}


def get_conversation_observation(study_id: str) -> ChatObservation | None:
    conversation_doc = conversation_docs.find_one({"study_id": study_id})

    if not conversation_doc:
        return None

    payload = conversation_doc.get("payload")

    if not payload:
        return None

    strategy = payload.get("strategy")
    signals = payload.get("signals")

    if not strategy or not signals:
        return None

    return ChatObservation(observation=strategy_observation[strategy](signals))
