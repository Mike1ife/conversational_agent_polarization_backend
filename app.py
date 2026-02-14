from fastapi import FastAPI, HTTPException
from src.utils import study_id_is_valid, advance_user_state
from src.schema import UserState


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Vercel"}


@app.get("/validate/{study_id}", tags=["General"])
def validate_study_id(study_id: str):
    if study_id_is_valid(study_id=study_id):
        return {"message": "Study ID Found"}
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")


@app.post("/advance/{study_id}", tags=["General"])
def advance_user_state_route(study_id: str, next_state: UserState):
    advance_user_state(study_id=study_id, next_state=next_state)
    return {"message": "Advance User State Successfully"}
