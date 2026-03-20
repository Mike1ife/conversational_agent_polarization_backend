from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.utils.user import study_id_is_valid
from app.utils.chat import llm_inference
from app.schema import ChatRequest

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/chat/{study_id}/complete")
def llm_inference_route(study_id: str, chat_request: ChatRequest):
    if study_id_is_valid(study_id=study_id):
        return StreamingResponse(
            llm_inference(study_id=study_id, chat_request=chat_request),
            media_type="text/event-stream",
        )
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")
