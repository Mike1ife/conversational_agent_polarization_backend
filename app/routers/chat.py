from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.utils.user import study_id_is_valid
from app.utils.chat import get_chat_history, get_conversation_id, llm_inference
from app.schema import ChatRequest

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/history/{study_id}")
def get_conversation_history_route(study_id: str):
    if not study_id_is_valid(study_id=study_id):
        raise HTTPException(status_code=404, detail="Study ID Not Found")

    conversation_id = get_conversation_id(study_id=study_id)
    if not conversation_id:
        return []

    return get_chat_history(conversation_id=conversation_id)


@router.post("/complete/{study_id}")
def llm_inference_route(study_id: str, chat_request: ChatRequest):
    if study_id_is_valid(study_id=study_id):
        return StreamingResponse(
            llm_inference(study_id=study_id, chat_request=chat_request),
            media_type="text/event-stream",
        )
    else:
        raise HTTPException(status_code=404, detail="Study ID Not Found")
