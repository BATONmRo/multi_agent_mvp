from mas.agents.base import BaseAgent
from mas.contracts import AgentResponse
from mas.state import PipelineState


class ReagentAgent(BaseAgent):
    name = "reagent"

    def run(self, state: PipelineState) -> AgentResponse:
        method = state.data.get("method")

        if not method:
            return {
                "status": "fail",
                "result": {},
                "reason": "No method found in state",
            }

        reagent_check = {
            "availability": "ok",
            "checked_items": [
                "Pd catalyst",
                "base",
                "solvent",
            ],
            "notes": "Demo reagent check passed",
        }

        return {
            "status": "ok",
            "result": reagent_check,
            "reason": "Reagents validated successfully",
        }