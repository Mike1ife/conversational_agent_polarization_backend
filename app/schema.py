from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Dict, Literal, Optional


class CaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class UserState(CaseModel):
    state: Literal[
        "not_started",
        "pre_survey",
        "to_intervention",
        "intervention",
        "to_post_survey",
        "post_survey",
        "complete",
    ]


class AgentCode(CaseModel):
    strategy: Literal[
        "common_identity", "personal_narrative", "misperception_correction"
    ]


class SurveyResponses(CaseModel):
    responses: Dict[str, str]


class UserParty(CaseModel):
    party: Literal["Republican", "Democrat"]


class ChatRequest(CaseModel):
    message: str


class ChatResponse(CaseModel):
    type: Literal["token", "done"]
    content: Optional[str]


class Message(CaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatMessage(CaseModel):
    role: str
    content: str | list

    def text_content(self) -> str:
        """Extract plain text from content, whether string or list format."""
        if isinstance(self.content, str):
            return self.content
        # Handle OpenAI multi-modal format: [{"type": "text", "text": "..."}]
        parts = []
        for item in self.content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return " ".join(parts)


class ChatCompletionRequest(CaseModel):
    study_id: str
    model: str = "common-identity"
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    session_id: str | None = (
        None  # pass back on subsequent turns for session continuity
    )
