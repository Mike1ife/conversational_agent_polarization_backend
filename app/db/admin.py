import os
import random
import string
from datetime import datetime, timezone

from app.db.db import user_docs
from app.schema import AgentStrategy

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
                "agent_strategy": random.choice(list(Strategy)).value,
                "state": "not_started",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            for _ in range(count)
        ]
    )


def generate_users_by_agent_strategy(agent_strategy: AgentStrategy, count: int):
    """Pre-experiment where start with intervention"""
    user_docs.insert_many(
        [
            {
                "study_id": "".join(
                    random.choices(string.ascii_letters + string.digits, k=6)
                ),
                "agent_strategy": agent_strategy.strategy,
                "state": "intervention",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            for _ in range(count)
        ]
    )


def get_availble_users_by_agent_strategy(agent_strategy: AgentStrategy) -> list:
    """Get available user list by agent strategy (Pre-experiment Setting)"""
    cursor = user_docs.find(
        {"agent_strategy": agent_strategy.strategy},
        {"_id": 0, "study_id": 1, "state": "intervention"},
    )

    return [f"{base_url}/{user_doc["study_id"]}" for user_doc in cursor]


def get_complete_users_by_agent_strategy(agent_strategy: AgentStrategy) -> list:
    """Get complete user list by agent strategy (Pre-experiment Setting)"""
    cursor = user_docs.find(
        {"agent_strategy": agent_strategy.strategy},
        {"_id": 0, "study_id": 1, "state": "complete"},
    )

    return [user_doc["study_id"] for user_doc in cursor]
