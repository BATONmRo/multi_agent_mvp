from prompts import chat_json

def run(self, state: PipelineState) -> AgentResponse:
    route = state.data.get("route")

    if not route:
        return {
            "status": "fail",
            "result": {},
            "reason": "No route found in state",
        }

    system_prompt = """
You are a synthesis method expert.
Return ONLY valid JSON.

Format:
{
  "status": "ok",
  "result": {
    "route_used": "...",
    "method_summary": "...",
    "references": ["...", "..."]
  },
  "reason": "..."
}
"""

    user_prompt = f"Route: {route}"

    result = chat_json(system_prompt, user_prompt)

    if "status" not in result:
        return {
            "status": "fail",
            "result": {"raw": result},
            "reason": "Invalid model response",
        }

    return result