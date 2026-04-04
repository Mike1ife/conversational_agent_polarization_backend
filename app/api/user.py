from fastapi import APIRouter, HTTPException
from app.db.user import (
    study_id_is_valid,
    get_user_state,
    get_user_agent_strategy,
    advance_user_state,
    get_user_party,
    save_user_party,
)
from app.schema import UserState, UserParty

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


@router.get("/get/agent_strategy/{study_id}")
def get_user_agent_strategy_route(study_id: str):
    if study_id_is_valid(study_id=study_id):
        agent_strategy = get_user_agent_strategy(study_id=study_id)
        return agent_strategy.model_dump(by_alias=True)
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")


@router.get("/party/{study_id}")
def get_user_party_route(study_id: str):
    if study_id_is_valid(study_id=study_id):
        party = get_user_party(study_id=study_id)
        return party.model_dump(by_alias=True)
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")


@router.post("/advance/{study_id}")
def advance_user_state_route(study_id: str, next_state: UserState):
    if study_id_is_valid(study_id=study_id):
        advance_user_state(study_id=study_id, next_state=next_state)
        return {"message": "Advance User State Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")


@router.post("/party/{study_id}")
def save_user_party_route(study_id: str, user_party: UserParty):
    if study_id_is_valid(study_id=study_id):
        save_user_party(study_id=study_id, user_party=user_party)
        return {"message": "Save User Party Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")
