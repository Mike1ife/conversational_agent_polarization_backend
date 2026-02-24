from fastapi import APIRouter, HTTPException
from app.utils import (
    study_id_is_valid,
    get_user_state,
    advance_user_state,
)
from app.schema import UserState

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/validate/{study_id}")
def validate_study_id(study_id: str):
    if study_id_is_valid(study_id=study_id):
        return {"message": "Study ID Found"}
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")


@router.get("/state/{study_id}")
def get_user_state_route(study_id: str):
    if study_id_is_valid(study_id=study_id):
        curr_state = get_user_state(study_id=study_id)
        return curr_state.model_dump(by_alias=True)
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")


@router.post("/advance/{study_id}")
def advance_user_state_route(study_id: str, next_state: UserState):
    if study_id_is_valid(study_id=study_id):
        advance_user_state(study_id=study_id, next_state=next_state)
        return {"message": "Advance User State Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")
