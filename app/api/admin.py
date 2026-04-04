from fastapi import APIRouter, HTTPException
from app.db.user import (
    generate_users,
    generate_users_by_agent_strategy,
    get_users_by_agent_strategy,
)
from app.schema import AgentStrategy

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/generate/{count}")
def generate_users_route(count: int):
    generate_users(count=count)
    return {"message": "Generate Users Successfully"}


@router.post("/generate/agent_strategy/{count}")
def generate_users_by_agent_strategy_route(agent_strategy: AgentStrategy, count: int):
    generate_users_by_agent_strategy(agent_strategy=agent_strategy, count=count)
    return {"message": f"Generate Users for {agent_strategy} Successfully"}


@router.post("/list/users/agent_strategy")
def get_users_by_agent_strategy_route(agent_strategy: AgentStrategy):
    return get_users_by_agent_strategy(agent_strategy=agent_strategy)
