from typing import Any, Dict, List


class AgentMemory:
    def __init__(self):
        self.store: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.store.get(key, default)

    def add_event(self, agent: str, action: str, payload: Any) -> None:
        self.history.append(
            {
                "agent": agent,
                "action": action,
                "payload": payload,
            }
        )

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def to_dict(self) -> Dict[str, Any]:
        return {
            "store": self.store,
            "history": self.history,
        }


def build_memory_summary(memory: AgentMemory) -> str:
    parts = []

    input_task = memory.get("input_task")
    if input_task:
        parts.append(f"Input task: {input_task}")

    parsed_task = memory.get("parsed_task")
    if parsed_task:
        parts.append(f"Parsed target: {parsed_task.get('target')}")

    extracted_reagents = memory.get("extracted_reagents")
    if extracted_reagents:
        parts.append(f"Extracted reagents: {', '.join(extracted_reagents)}")

    methods_result = memory.get("methods_result")
    if methods_result:
        parts.append("Methods context available")

    reagents_result = memory.get("reagents_result")
    if reagents_result:
        parts.append("Reagents context available")

    final_status = memory.get("final_status")
    if final_status:
        parts.append(f"Current status: {final_status}")

    return "\n".join(parts)