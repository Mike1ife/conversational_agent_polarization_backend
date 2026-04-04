from app.db.db import user_docs
from app.schema import UserState, UserParty, AgentStrategy


def study_id_is_valid(study_id: str) -> bool:
    return user_docs.count_documents({"study_id": study_id}, limit=1) > 0


def get_user_agent_strategy(study_id: str) -> AgentStrategy:
    """Get user's agent strategy by study_id"""
    user_doc = user_docs.find_one(
        {"study_id": study_id},
        {"_id": 0, "agent_strategy": 1},
    )

    return AgentStrategy(strategy=user_doc.get("agent_strategy", "common_identity"))


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
