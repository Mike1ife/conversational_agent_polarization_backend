import random
from datetime import datetime, timezone

from app.db.admin import generate_study_id
from app.db.documents import user_docs

from app.agent.strategies import Strategy


def generate_experiment_user() -> str:
    """Generate a user for pre-experiment"""
    study_id = generate_study_id()
    user_docs.insert_one(
        {
            "study_id": study_id,
            "type": "experiment",
            "strategy": "personal_narrative",  # random.choice(list(Strategy)).value,
            "state": "intervention",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )
    return study_id
