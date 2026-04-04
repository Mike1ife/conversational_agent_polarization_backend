from fastapi import APIRouter, HTTPException
from app.db.user import (
    generate_users,
    generate_users_by_agent_strategy,
    get_user_agent_strategy,
    get_users_by_agent_strategy,
    study_id_is_valid,
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


@router.get("/get/agent_strategy/{study_id}")
def get_user_agent_strategy_route(study_id: str):
    if study_id_is_valid(study_id=study_id):
        agent_strategy = get_user_agent_strategy(study_id=study_id)
        return agent_strategy.model_dump(by_alias=True)
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")


@router.post("/list/users/agent_strategy")
def get_users_by_agent_strategy_route(agent_strategy: AgentStrategy):
    return get_users_by_agent_strategy(agent_strategy=agent_strategy)
