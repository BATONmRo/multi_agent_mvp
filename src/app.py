from mas.orchestrator import Orchestrator
from mas.utils.logger import print_history


def main() -> None:
    target = "aspirin_demo_target"

    orchestrator = Orchestrator()
    state = orchestrator.run(target=target)

    print_history(state)

    print("=== FINAL OUTPUT ===")
    print(state.final_output)


if __name__ == "__main__":
    main()