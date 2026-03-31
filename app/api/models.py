import time

from fastapi import APIRouter

router = APIRouter(tags=["Model"])

_MODELS = [
    {
        "id": "common-identity",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "partisan-animosity-study",
        "permission": [],
        "root": "common-identity",
        "parent": None,
    },
    {
        "id": "personal-narrative",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "partisan-animosity-study",
        "permission": [],
        "root": "personal-narrative",
        "parent": None,
    },
    {
        "id": "misperception-correction",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "partisan-animosity-study",
        "permission": [],
        "root": "misperception-correction",
        "parent": None,
    },
]


@router.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible format)."""
    return {"object": "list", "data": _MODELS}
