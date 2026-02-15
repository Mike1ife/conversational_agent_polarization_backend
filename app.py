from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.utils import study_id_is_valid, get_user_state, advance_user_state
from src.schema import UserState


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://conversational-agent-polarization.vercel.app/",
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
