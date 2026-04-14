from datetime import datetime, timezone

from app.schema import Message
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
    response = conversation_doc.get("response")

    messages = payload.get("messages") or payload.get("message") or []
    history = _coerce_messages(messages)

    if response and (
        not history
        or history[-1].role != "assistant"
        or history[-1].content != response
    ):
        history.append(Message(role="assistant", content=response))

    return history
