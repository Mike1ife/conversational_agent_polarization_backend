from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Dict, Literal


class CaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class UserState(CaseModel):
    state: Literal[
        "not_started", "pre_survey", "conversation", "post_survey", "complete"
    ]


class SurveyResponses(CaseModel):
    responses: Dict[str, str]
