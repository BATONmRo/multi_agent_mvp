
from pydantic import BaseModel
from typing import List
from typing import Any


class RouteStep(BaseModel):
    reaction: str
    reagents: List[str]
    conditions: str

class RouteAgentOutput(BaseModel):
    target: str
    steps: List[RouteStep]
    confidence: float

class ValidationOutput(BaseModel):
    valid: bool
    issues: List[str]
    suggestions: List[str]

class PipelineResult(BaseModel):
    input_task: str
    route: Any
    validation: Any
    methods_result: dict | None = None
    reagents_result: dict | None = None
    final_status: str

class BaselineOutput(BaseModel):
    task: str
    answer: str