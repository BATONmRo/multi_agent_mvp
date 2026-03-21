from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HistoryItem:
    agent: str
    status: str
    result: Dict[str, Any]
    reason: str


@dataclass
class PipelineState:
    input: Dict[str, Any]
    current_step: str = "route"
    data: Dict[str, Any] = field(default_factory=dict)
    history: List[HistoryItem] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    done: bool = False
    final_output: Optional[Dict[str, Any]] = None


def init_state(target: str) -> PipelineState:
    return PipelineState(
        input={"target": target},
        current_step="route",
        data={},
        history=[],
        errors=[],
        done=False,
        final_output=None,
    )