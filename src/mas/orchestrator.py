from mas.agents.method_agent import MethodAgent
from mas.agents.reagent_agent import ReagentAgent
from mas.agents.route_agent import RouteAgent
from mas.state import PipelineState, init_state
from mas.utils.logger import log_step


class Orchestrator:
    def __init__(self) -> None:
        self.route_agent = RouteAgent()
        self.method_agent = MethodAgent()
        self.reagent_agent = ReagentAgent()

    def run(self, target: str) -> PipelineState:
        state = init_state(target)

        while not state.done:
            if state.current_step == "route":
                response = self.route_agent.run(state)
                log_step(
                    state=state,
                    agent="route",
                    status=response["status"],
                    result=response["result"],
                    reason=response["reason"],
                )

                if response["status"] == "ok":
                    state.data["route"] = response["result"]
                    state.current_step = "method"
                else:
                    state.errors.append(
                        {"step": "route", "reason": response["reason"]}
                    )
                    state.done = True
                    state.final_output = {
                        "status": "fail",
                        "reason": response["reason"],
                    }

            elif state.current_step == "method":
                response = self.method_agent.run(state)
                log_step(
                    state=state,
                    agent="method",
                    status=response["status"],
                    result=response["result"],
                    reason=response["reason"],
                )

                if response["status"] == "ok":
                    state.data["method"] = response["result"]
                    state.current_step = "reagent"
                else:
                    state.errors.append(
                        {"step": "method", "reason": response["reason"]}
                    )
                    state.current_step = "route"

            elif state.current_step == "reagent":
                response = self.reagent_agent.run(state)
                log_step(
                    state=state,
                    agent="reagent",
                    status=response["status"],
                    result=response["result"],
                    reason=response["reason"],
                )

                if response["status"] == "ok":
                    state.data["reagent"] = response["result"]
                    state.done = True
                    state.final_output = {
                        "status": "ok",
                        "target": state.input["target"],
                        "route": state.data.get("route"),
                        "method": state.data.get("method"),
                        "reagent": state.data.get("reagent"),
                    }
                else:
                    state.errors.append(
                        {"step": "reagent", "reason": response["reason"]}
                    )
                    state.current_step = "method"

            else:
                state.errors.append(
                    {"step": state.current_step, "reason": "Unknown step"}
                )
                state.done = True
                state.final_output = {
                    "status": "fail",
                    "reason": f"Unknown step: {state.current_step}",
                }

        return state