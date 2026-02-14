from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Optional, Dict, Literal, Union


class CaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class UserState(CaseModel):
    state: Literal[
        "not_started", "pre_survey", "intervention", "post_survey", "complete"
    ]
