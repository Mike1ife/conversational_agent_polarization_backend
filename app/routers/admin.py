from fastapi import APIRouter
from app.utils import generate_users

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/generate/{count}")
def generate_users_route(count: int):
    generate_users(count=count)
    return {"message": "Generate Users Successfully"}
