from mas.agents.base import BaseAgent
from mas.contracts import AgentResponse
from mas.state import PipelineState


class MethodAgent(BaseAgent):
    name = "method"

    def run(self, state: PipelineState) -> AgentResponse:
        route = state.data.get("route")

        if not route:
            return {
                "status": "fail",
                "result": {},
                "reason": "No route found in state",
            }

        method_result = {
            "route_used": route.get("route_summary", ""),
            "method_summary": "Retrieved demo methodology from local corpus",
            "references": [
                "demo_doc_001",
                "demo_doc_002",
            ],
        }

        return {
            "status": "ok",
            "result": method_result,
            "reason": "Methodology retrieved successfully",
        }