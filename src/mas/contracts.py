from typing import Any, Dict, Literal, TypedDict


AgentStatus = Literal["ok", "fail"]


class AgentResponse(TypedDict):
    status: AgentStatus
    result: Dict[str, Any]
    reason: str