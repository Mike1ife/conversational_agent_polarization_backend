from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.utils import (
    generate_users,
    study_id_is_valid,
    get_user_state,
    advance_user_state,
    save_pre_survey,
    save_post_survey,
)
from src.schema import UserState, SurveyResponses


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://conversational-agent-polarization.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Vercel"}


@app.post("/generate/{count}", tags=["Admin"])
def generate_users_route(count: int):
    generate_users(count=count)
    return {"message": "Generate Users Successfully"}


@app.get("/validate/{study_id}", tags=["General"])
def validate_study_id(study_id: str):
    if study_id_is_valid(study_id=study_id):
        return {"message": "Study ID Found"}
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")


@app.get("/state/{study_id}", tags=["General"])
def get_user_state_route(study_id: str):
    curr_state = get_user_state(study_id=study_id)
    return curr_state.model_dump(by_alias=True)


@app.post("/advance/{study_id}", tags=["General"])
def advance_user_state_route(study_id: str, next_state: UserState):
    advance_user_state(study_id=study_id, next_state=next_state)
    return {"message": "Advance User State Successfully"}


@app.post("/survey/pre/{study_id}", tags=["Survey"])
def save_pre_survey_route(study_id: str, survey_responses: SurveyResponses):
    save_pre_survey(study_id=study_id, survey_responses=survey_responses)
    return {"message": "Save Pre-Survey Responses Successfully"}


@app.post("/survey/post/{study_id}", tags=["Survey"])
def save_post_survey_route(study_id: str, survey_responses: SurveyResponses):
    save_post_survey(study_id=study_id, survey_responses=survey_responses)
    return {"message": "Save Post-Survey Responses Successfully"}
