from mas.state import HistoryItem, PipelineState


def log_step(
    state: PipelineState,
    agent: str,
    status: str,
    result: dict,
    reason: str,
) -> None:
    state.history.append(
        HistoryItem(
            agent=agent,
            status=status,
            result=result,
            reason=reason,
        )
    )


def print_history(state: PipelineState) -> None:
    print("\n=== PIPELINE LOG ===")
    for idx, item in enumerate(state.history, start=1):
        print(
            f"{idx}. [{item.agent}] status={item.status} "
            f"reason='{item.reason}' result={item.result}"
        )
    if state.errors:
        print("\n=== ERRORS ===")
        for err in state.errors:
            print(err)
    print("====================\n")