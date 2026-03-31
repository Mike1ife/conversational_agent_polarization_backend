from __future__ import annotations

import json
import time
import uuid

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from app.schema import ChatCompletionRequest
from app.agent.pipeline import AgentPipeline
from app.config import settings
from app.llm.registry import get_provider
from app.db.user import study_id_is_valid
from app.db.conversation import get_chat_history, get_conversation_id


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/history/{study_id}")
def get_conversation_history_route(study_id: str):
    if not study_id_is_valid(study_id=study_id):
        raise HTTPException(status_code=404, detail="Study ID Not Found")

    conversation_id = get_conversation_id(study_id=study_id)
    if not conversation_id:
        return []

    return get_chat_history(conversation_id=conversation_id)


# Lazy-initialized pipeline singleton
_pipeline: AgentPipeline | None = None


def _get_pipeline() -> AgentPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = AgentPipeline(llm=get_provider())
    return _pipeline


# Map OpenAI-style model IDs to internal condition names
_MODEL_TO_CONDITION = {
    "common-identity": "common_identity",
    "personal-narrative": "personal_narrative",
    "misperception-correction": "misperception_correction",
}


_UTILITY_PHRASES = (
    "generate a brief",
    "purposeful title",
    "generate a title",
    "summarize this conversation",
    "conversation title",
)


def _is_utility_request(messages: list[dict]) -> bool:
    """Return True if this looks like a frontend meta-request (title gen, summary, etc.)."""
    last_user = next(
        (m["content"] for m in reversed(messages) if m.get("role") == "user"), ""
    )
    low = last_user.lower()
    return any(phrase in low for phrase in _UTILITY_PHRASES)


@router.post("/completions")
async def chat_completions(request: Request):
    """OpenAI-compatible chat completions endpoint."""
    body = await request.json()
    req = ChatCompletionRequest(**body)

    pipeline = _get_pipeline()

    # Derive condition from model ID, fall back to config default
    strategy_name = _MODEL_TO_CONDITION.get(req.model, settings.default_strategy)

    messages = [{"role": m.role, "content": m.text_content()} for m in req.messages]
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

    # Bypass the agent pipeline for frontend utility requests (title gen, etc.)
    if _is_utility_request(messages):
        return await _utility_response(
            pipeline, messages, completion_id, req.model, req.stream
        )

    session_id = pipeline.resolve_session_id(messages, strategy_name, req.session_id)

    if req.stream:
        return StreamingResponse(
            _stream_response(
                pipeline, messages, strategy_name, completion_id, req.model, session_id
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        # Non-streaming: collect full response
        full_response = []
        async for token in pipeline.process_turn(
            messages=messages,
            strategy_name=strategy_name,
            session_id=session_id,
        ):
            if token is AgentPipeline.KEEP_ALIVE:
                continue
            full_response.append(token)

        return {
            "id": completion_id,
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "session_id": session_id,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "".join(full_response),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }


async def _stream_response(
    pipeline: AgentPipeline,
    messages: list[dict],
    strategy_name: str,
    completion_id: str,
    model_id: str = "common-identity",
    session_id: str | None = None,
):
    """Generate SSE stream in OpenAI chunk format."""
    created = int(time.time())

    # Initial chunk with role and session_id for the frontend to store
    initial_chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_id,
        "session_id": session_id,
        "choices": [
            {
                "index": 0,
                "delta": {"role": "assistant", "content": ""},
                "finish_reason": None,
            }
        ],
    }
    yield f"data: {json.dumps(initial_chunk)}\n\n"

    # Stream content tokens (pipeline may yield KEEP_ALIVE during blocking work)
    async for token in pipeline.process_turn(
        messages=messages,
        strategy_name=strategy_name,
        session_id=session_id,
    ):
        # Keep-alive: send SSE comment to prevent proxy/client timeout
        if token is AgentPipeline.KEEP_ALIVE:
            yield ": keep-alive\n\n"
            continue

        chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_id,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": token},
                    "finish_reason": None,
                }
            ],
        }
        yield f"data: {json.dumps(chunk)}\n\n"

    # Final chunk
    final_chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_id,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop",
            }
        ],
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"


async def _utility_response(
    pipeline: AgentPipeline,
    messages: list[dict],
    completion_id: str,
    model_id: str,
    stream: bool,
):
    """Handle frontend utility requests (title gen, summaries) via direct LLM call — no pipeline, no logging."""
    from app.llm.base import Message as LLMMessage

    llm_messages = [LLMMessage(role=m["role"], content=m["content"]) for m in messages]
    response = await pipeline.llm.complete(llm_messages)

    if stream:

        async def _gen():
            created = int(time.time())
            for chunk_text in [response]:
                yield f"data: {json.dumps({'id': completion_id, 'object': 'chat.completion.chunk', 'created': created, 'model': model_id, 'choices': [{'index': 0, 'delta': {'content': chunk_text}, 'finish_reason': None}]})}\n\n"
            yield f"data: {json.dumps({'id': completion_id, 'object': 'chat.completion.chunk', 'created': created, 'model': model_id, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            _gen(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_id,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
