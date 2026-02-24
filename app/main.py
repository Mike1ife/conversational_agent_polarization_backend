from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, user, survey

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

app.include_router(admin.router)
app.include_router(user.router)
app.include_router(survey.router)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Heroku/Vercel"}
