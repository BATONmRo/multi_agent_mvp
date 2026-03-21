
from pydantic import BaseModel
from typing import List

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