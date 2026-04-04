from fastapi import APIRouter
from app.db.admin import (
    generate_users,
    generate_users_by_agent_strategy,
    get_availble_users_by_agent_strategy,
    get_complete_users_by_agent_strategy,
)
from app.schema import AgentStrategy

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/generate/{count}")
def generate_users_route(count: int):
    generate_users(count=count)
    return {"message": "Generate Users Successfully"}


@router.post("/agent_strategy/generate/{count}")
def generate_users_by_agent_strategy_route(agent_strategy: AgentStrategy, count: int):
    generate_users_by_agent_strategy(agent_strategy=agent_strategy, count=count)
    return {"message": f"Generate Users for {agent_strategy} Successfully"}


@router.post("/agent_strategy/list/users/available")
def get_availble_users_by_agent_strategy_route(agent_strategy: AgentStrategy):
    return get_availble_users_by_agent_strategy(agent_strategy=agent_strategy)


@router.post("/agent_strategy/list/users/complete")
def get_complete_users_by_agent_strategy_route(agent_strategy: AgentStrategy):
    return get_complete_users_by_agent_strategy(agent_strategy=agent_strategy)
