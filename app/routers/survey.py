from fastapi import APIRouter
from app.utils import save_pre_survey, save_post_survey
from app.schema import SurveyResponses

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.post("/pre/{study_id}")
def save_pre_survey_route(study_id: str, survey_responses: SurveyResponses):
    save_pre_survey(study_id=study_id, survey_responses=survey_responses)
    return {"message": "Save Pre-Survey Responses Successfully"}


@router.post("/post/{study_id}")
def save_post_survey_route(study_id: str, survey_responses: SurveyResponses):
    save_post_survey(study_id=study_id, survey_responses=survey_responses)
    return {"message": "Save Post-Survey Responses Successfully"}
