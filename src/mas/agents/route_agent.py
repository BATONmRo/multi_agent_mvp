from prompts import chat_json

def run(self, state: PipelineState) -> AgentResponse:
    target = state.input["target"]

    if not target:
        return {
            "status": "fail",
            "result": {},
            "reason": "Target molecule is empty",
        }

    system_prompt = """
You are a retrosynthesis planning agent.
Return ONLY valid JSON.

Format:
{
  "status": "ok",
  "result": {
    "target": "...",
    "route_summary": "...",
    "steps": ["...", "...", "..."]
  },
  "reason": "..."
}
"""

    user_prompt = f"Target molecule: {target}"

    result = chat_json(system_prompt, user_prompt)

    if "status" not in result:
        return {
            "status": "fail",
            "result": {"raw": result},
            "reason": "Invalid model response",
        }

    return result

def run(self, state: PipelineState) -> AgentResponse:
    target = state.input["target"]

    if not target:
        return {
            "status": "fail",
            "result": {},
            "reason": "Target molecule is empty",
        }

    system_prompt = """
You are a retrosynthesis planning agent.
Return ONLY valid JSON.

Format:
{
  "status": "ok",
  "result": {
    "target": "...",
    "route_summary": "...",
    "steps": ["...", "...", "..."]
  },
  "reason": "..."
}
"""

    user_prompt = f"Target molecule: {target}"

    result = chat_json(system_prompt, user_prompt)

    if "status" not in result:
        return {
            "status": "fail",
            "result": {"raw": result},
            "reason": "Invalid model response",
        }

    return result