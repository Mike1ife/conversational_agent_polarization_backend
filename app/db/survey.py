from app.db.documents import user_docs
from app.schema import SurveyResponses


def save_pre_survey(study_id: str, survey_responses: SurveyResponses):
    user_docs.update_one(
        {"study_id": study_id},
        {
            "$set": {"pre_survey": survey_responses.responses},
            "$currentDate": {"updated_at": True},
        },
    )


def save_post_survey(study_id: str, survey_responses: SurveyResponses):
    user_docs.update_one(
        {"study_id": study_id},
        {
            "$set": {"post_survey": survey_responses.responses},
            "$currentDate": {"updated_at": True},
        },
    )
