from mas.agents.base import BaseAgent
from mas.contracts import AgentResponse
from mas.state import PipelineState


class RouteAgent(BaseAgent):
    name = "route"

    def run(self, state: PipelineState) -> AgentResponse:
        target = state.input["target"]

        if not target:
            return {
                "status": "fail",
                "result": {},
                "reason": "Target molecule is empty",
            }

        route_plan = {
            "target": target,
            "route_summary": f"Draft synthesis route for {target}",
            "steps": [
                "Identify core scaffold",
                "Suggest precursor disconnections",
                "Select candidate route",
            ],
        }

        return {
            "status": "ok",
            "result": route_plan,
            "reason": "Route drafted successfully",
        }