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
