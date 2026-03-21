from abc import ABC, abstractmethod

from mas.contracts import AgentResponse
from mas.state import PipelineState


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, state: PipelineState) -> AgentResponse:
        raise NotImplementedError