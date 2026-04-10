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
            "$set": {"payload": entry, "updated_at": now},
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )


def get_chat_history(study_id: str) -> list:
    conversation_doc = conversation_docs.find_one({"study_id": study_id})

    if not conversation_doc:
        return []

    payload = conversation_doc.get("payload", None)
    response = conversation_doc.get("response", None)

    if not payload or not response:
        return []

    messages = payload.get("messages", [])

    history = []

    for msg in messages:
        history.append(Message(role=msg["role"], content=msg["content"]))
    history.append(Message(role="assistant", content=response))

    return history
