import os
from fastapi import APIRouter, HTTPException
from app.db.admin import (
    generate_users,
    generate_users_by_agent_strategy,
    get_state_users_by_agent_strategy,
)
from app.schema import (
    GenerateUserRequest,
    GenerateUserByStrategyRequest,
    GetUserByStrategyRequest,
)

router = APIRouter(prefix="/admin", tags=["Admin"])
admin_password = os.getenv("ADMIN_PASSWORD")


@router.post("/generate")
def generate_users_route(request: GenerateUserRequest):
    if request.password != admin_password:
        raise HTTPException(status_code=403, detail="Invalid admin password")
    generate_users(count=request.count)
    return {"message": "Generate Users Successfully"}


@router.post("/agent_strategy/generate")
def generate_users_by_agent_strategy_route(request: GenerateUserByStrategyRequest):
    if request.password != admin_password:
        raise HTTPException(status_code=403, detail="Invalid admin password")
    generate_users_by_agent_strategy(
        agent_strategy=request.strategy, count=request.count
    )
    return {"message": f"Generate Users for {request.strategy} Successfully"}


@router.post("/agent_strategy/list/users")
def get_state_users_by_agent_strategy_route(request: GetUserByStrategyRequest):
    if request.password != admin_password:
        raise HTTPException(status_code=403, detail="Invalid admin password")
    return get_state_users_by_agent_strategy(
        state=request.state, agent_strategy=request.strategy
    )
