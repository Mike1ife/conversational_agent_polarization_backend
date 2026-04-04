import random
import string
from datetime import datetime, timezone

from app.db.db import user_docs
from app.schema import UserState, UserParty, AgentStrategy

from app.agent.strategies import Strategy


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


def get_user_agent_strategy(study_id: str) -> AgentStrategy:
    """Get user's agent strategy by study_id"""
    user_doc = user_docs.find_one(
        {"study_id": study_id},
        {"_id": 0, "agent_strategy": 1},
    )

    return AgentStrategy(strategy=user_doc.get("agent_strategy", "common_identity"))


def get_users_by_agent_strategy(agent_strategy: AgentStrategy) -> list:
    """Get user list by agent strategy"""
    cursor = user_docs.find(
        {"agent_strategy": agent_strategy.strategy},
        {"_id": 0, "study_id": 1},
    )

    return [user_doc["study_id"] for user_doc in cursor]


def study_id_is_valid(study_id: str) -> bool:
    return user_docs.count_documents({"study_id": study_id}, limit=1) > 0


def get_user_state(study_id: str) -> UserState:
    user_doc = user_docs.find_one(
        {"study_id": study_id},
        {"_id": 0, "state": 1},
    )

    return UserState(state=user_doc.get("state", "not_started"))


def get_user_party(study_id: str) -> UserParty:
    user_doc = user_docs.find_one(
        {"study_id": study_id},
        {"_id": 0, "party": 1},
    )

    return UserParty(party=user_doc.get("party"))


def advance_user_state(study_id: str, next_state: UserState):
    user_docs.update_one(
        {"study_id": study_id},
        {"$set": {"state": next_state.state}, "$currentDate": {"updated_at": True}},
    )


def save_user_party(study_id: str, user_party: UserParty):
    user_docs.update_one(
        {"study_id": study_id},
        {"$set": {"party": user_party.party}, "$currentDate": {"updated_at": True}},
    )
