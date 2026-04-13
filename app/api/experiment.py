from fastapi import APIRouter
from app.db.experiment import generate_experiment_user


router = APIRouter(prefix="/experiment", tags=["Experiment"])


@router.post("/generate")
def generate_experiment_user_route():
    """Generate a User for Pre-experiment"""
    study_id = generate_experiment_user()
    return {"id": study_id}
