import os
import random
import string
from datetime import datetime, timezone

from app.db.db import chat_docs, message_docs, user_docs
from app.schema import GetUserResponse

from app.agent.strategies import Strategy

base_url = os.getenv("PLATFORM_URL")


def generate_users(count: int):
    """Generate user randomly"""
    user_docs.insert_many(
        [
            {
                "study_id": "".join(
                    random.choices(string.ascii_letters + string.digits, k=6)
                ),
                "strategy": random.choice(list(Strategy)).value,
                "state": "not_started",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            for _ in range(count)
        ]
    )


def generate_users_by_agent_strategy(strategy: str, count: int):
    """Pre-experiment where start with intervention"""
    user_docs.insert_many(
        [
            {
                "study_id": "".join(
                    random.choices(string.ascii_letters + string.digits, k=6)
                ),
                "strategy": strategy,
                "state": "intervention",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            for _ in range(count)
        ]
    )


def get_state_users_by_agent_strategy(state: str, strategy: str) -> list:
    """Get available user list by agent strategy (Pre-experiment Setting)"""
    cursor = user_docs.find(
        {"state": state},
        {"agent_strategy": strategy},
        {"_id": 0, "study_id": 1, "state": "intervention"},
    )

    return [
        GetUserResponse(
            study_id=user_doc["study_id"], url=f"{base_url}/{user_doc['study_id']}"
        )
        for user_doc in cursor
    ]


def delete_all_users() -> int:
    """Delete all users and their associated conversations/messages."""
    deleted_users = user_docs.delete_many({}).deleted_count
    chat_docs.delete_many({})
    message_docs.delete_many({})
    return deleted_users


def delete_user_by_id(study_id: str) -> int:
    """Delete one user and associated conversations/messages by study_id."""
    user_docs.delete_one({"study_id": study_id}).deleted_count
    chat_docs.delete_many({"study_id": study_id})
    message_docs.delete_many({"study_id": study_id})
