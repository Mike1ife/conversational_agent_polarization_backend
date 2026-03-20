from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, AIMessage

from app.schema import ChatResponse, ChatRequest, Message
from app.utils.db import chat_docs, message_docs
from app.utils.model import llm


def initialize_conversation(study_id: str):
    chat_docs.insert_one(
        {
            "study_id": study_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )


def get_conversation(study_id: str) -> dict:
    return chat_docs.find_one({"study_id": study_id})


def get_conversation_id(study_id: str) -> str | None:
    conversation = chat_docs.find_one({"study_id": study_id})
    if not conversation:
        return None
    return str(conversation["_id"])


def create_message(conversation_id: str, role: str, content: str) -> dict:
    return {
        "conversation_id": conversation_id,
        "role": role,  # "user" | "assistant"
        "content": content,
        "created_at": datetime.now(timezone.utc),
    }


def save_user_message(conversation_id: str, content: str):
    message_docs.insert_one(create_message(conversation_id, "user", content))


def save_ai_message(conversation_id: str, content: str):
    message_docs.insert_one(create_message(conversation_id, "assistant", content))


def get_chat_history(conversation_id: str) -> list:
    messages = message_docs.find({"conversation_id": conversation_id}).sort(
        "created_at", 1
    )

    history = []

    for msg in messages:
        history.append(Message(role=msg["role"], content=msg["content"]))

    return history


def get_chat_history_langchain(conversation_id: str) -> list:
    messages = message_docs.find({"conversation_id": conversation_id}).sort(
        "created_at", 1
    )

    history = []

    for msg in messages:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        else:
            history.append(AIMessage(content=msg["content"]))

    return history


def llm_inference(study_id: str, chat_request: ChatRequest):
    conversation = get_conversation(study_id)

    if not conversation:
        initialize_conversation(study_id)
        conversation = get_conversation(study_id)

    conversation_id = str(conversation["_id"])

    save_user_message(conversation_id, chat_request.message)

    history = get_chat_history_langchain(conversation_id)

    full_response = ""

    for chunk in llm.stream(history):
        if not chunk.content:
            continue
        token = chunk.content
        full_response += token

        yield f"data: {ChatResponse(type='token', content=token).model_dump_json()}\n\n"

    # send done signal
    yield f"data: {ChatResponse(type='done', content=None).model_dump_json()}\n\n"

    save_ai_message(conversation_id, full_response)

    chat_docs.update_one(
        {"_id": conversation["_id"]},
        {"$currentDate": {"updated_at": True}},
    )
