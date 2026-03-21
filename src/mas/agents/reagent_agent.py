from prompts import chat_json

def run(self, state: PipelineState) -> AgentResponse:
    method = state.data.get("method")

    if not method:
        return {
            "status": "fail",
            "result": {},
            "reason": "No method found",
        }

    system_prompt = """
You are a reagent validation agent.
Return ONLY valid JSON.

Format:
{
  "status": "ok",
  "result": {
    "availability": "ok",
    "checked_items": ["...", "..."],
    "notes": "..."
  },
  "reason": "..."
}
"""

    user_prompt = f"Method: {method}"

    result = chat_json(system_prompt, user_prompt)

    if "status" not in result:
        return {
            "status": "fail",
            "result": {"raw": result},
            "reason": "Invalid model response",
        }

    return result