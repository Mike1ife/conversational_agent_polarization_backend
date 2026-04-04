from fastapi import APIRouter
from app.db.user import generate_users, generate_users_by_agent_code
from app.schema import AgentCode

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/generate/{count}")
def generate_users_route(count: int):
    generate_users(count=count)
    return {"message": "Generate Users Successfully"}


@router.post("/generate/agent_code/{count}")
def generate_users_by_agent_code_route(agent_code: AgentCode, count: int):
    generate_users_by_agent_code(agent_code=agent_code, count=count)
    return {"message": f"Generate Users for {agent_code} Successfully"}
