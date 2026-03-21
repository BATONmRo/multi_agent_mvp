from agents import route_agent, validator_agent, baseline_agent
from schemas import PipelineResult
from tools import tool_find_methods, check_reagents


def run_pipeline(target: str) -> PipelineResult:
    print("=== Шаг 1: route_agent ===")
    route_result = route_agent(target)
    print(route_result.model_dump_json(indent=2, ensure_ascii=False))

    print("\n=== Шаг 1.5: tools (methods + reagents) ===")
    methods_result = tool_find_methods(target)
    print("Methods found:")
    print(methods_result)

    reagents_result = {"checked": [], "issues": ["No reagents extracted"]}

    if methods_result.get("methods_found"):
        best_method = methods_result["methods_found"][0]
        reagents = best_method.get("reagents", [])
        reagents_result = check_reagents(reagents)

    print("Reagents check:")
    print(reagents_result)

    print("\n=== Шаг 2: validator_agent ===")
    validation_result = validator_agent(route_result)
    print(validation_result.model_dump_json(indent=2, ensure_ascii=False))

    final_status = "validated" if validation_result.valid else "needs_revision"

    return PipelineResult(
        input_task=target,
        route=route_result,
        validation=validation_result,
        methods_result=methods_result,
        reagents_result=reagents_result,
        final_status=final_status
    )


def main():
    target = "Составь маршрут синтеза аспирина из салициловой кислоты и укажи основные реагенты и условия"

    print("=== BASELINE ===")
    baseline_result = baseline_agent(target)
    print(baseline_result.model_dump_json(indent=2, ensure_ascii=False))

    print("\n=== MULTI-AGENT PIPELINE ===")
    pipeline_result = run_pipeline(target)

    print("\n=== FINAL PIPELINE RESULT ===")
    print(pipeline_result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()