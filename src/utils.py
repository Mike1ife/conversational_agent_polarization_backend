import os
import random
import string
from datetime import datetime, timezone
from pymongo.mongo_client import MongoClient

from src.schema import UserState, SurveyResponses

# Connection
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)

# Create db and collection at first insertion
db = client["study_db"]
user_docs = db["users"]


def study_id_is_valid(study_id: str) -> bool:
    return user_docs.count_documents({"study_id": study_id}, limit=1) > 0


def get_user_state(study_id: str) -> UserState:
    user_doc = user_docs.find_one(
        {"study_id": study_id},
        {"_id": 0, "state": 1},
    )

    return UserState(state=user_doc.get("state", "not_started"))


def advance_user_state(study_id: str, next_state: UserState):
    user_docs.update_one(
        {"study_id": study_id},
        {"$set": {"state": next_state.state}, "$currentDate": {"updated_at": True}},
    )


def save_pre_survey(study_id: str, survey_responses: SurveyResponses):
    user_docs.update_one(
        {"study_id": study_id},
        {
            "$set": {"pre_survey": survey_responses.responses},
            "$currentDate": {"updated_at": True},
        },
    )
