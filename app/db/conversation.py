from datetime import datetime, timezone

from app.schema import Message
from app.db.db import chat_docs, message_docs


def initialize_conversation(study_id: str):
    chat_docs.insert_one(
        {
            "study_id": study_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )


def get_or_create_conversation_id(study_id: str) -> str:
    conversation = chat_docs.find_one({"study_id": study_id})
    if conversation:
        return str(conversation["_id"])

    insert_result = chat_docs.insert_one(
        {
            "study_id": study_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )
    return str(insert_result.inserted_id)


def get_conversation(study_id: str) -> dict:
    return chat_docs.find_one({"study_id": study_id})


def get_conversation_id(study_id: str) -> str | None:
    conversation = chat_docs.find_one({"study_id": study_id})
    if not conversation:
        return None
    return str(conversation["_id"])


def create_message(
    conversation_id: str, study_id: str, role: str, content: str
) -> dict:
    return {
        "doc_type": "chat_message",
        "conversation_id": conversation_id,
        "study_id": study_id,
        "role": role,  # "user" | "assistant"
        "content": content,
        "created_at": datetime.now(timezone.utc),
    }


def save_user_message(conversation_id: str, study_id: str, content: str):
    message_docs.insert_one(create_message(conversation_id, study_id, "user", content))
    chat_docs.update_one(
        {"study_id": study_id},
        {"$set": {"updated_at": datetime.now(timezone.utc)}},
    )


def save_ai_message(conversation_id: str, study_id: str, content: str):
    message_docs.insert_one(
        create_message(conversation_id, study_id, "assistant", content)
    )
    chat_docs.update_one(
        {"study_id": study_id},
        {"$set": {"updated_at": datetime.now(timezone.utc)}},
    )


def save_turn_log(conversation_id: str, study_id: str, entry: dict):
    message_docs.insert_one(
        {
            "doc_type": "turn_log",
            "conversation_id": conversation_id,
            "study_id": study_id,
            "payload": entry,
            "created_at": datetime.now(timezone.utc),
        }
    )

    chat_docs.update_one(
        {"study_id": study_id},
        {"$set": {"updated_at": datetime.now(timezone.utc)}},
    )


def get_chat_history(conversation_id: str) -> list:
    messages = message_docs.find(
        {
            "conversation_id": conversation_id,
            "role": {"$in": ["user", "assistant"]},
            "$or": [
                {"doc_type": "chat_message"},
                {"doc_type": {"$exists": False}},
            ],
        }
    ).sort("created_at", 1)

    history = []

    for msg in messages:
        history.append(Message(role=msg["role"], content=msg["content"]))

    return history
