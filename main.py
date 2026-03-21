from agents import (
    task_parser_agent,
    route_agent,
    safety_agent,
    baseline_agent,
    methods_agent,
    reagents_agent,
)
from schemas import PipelineResult


def extract_all_reagents(route_result) -> list[str]:
    reagents = []

    for route in route_result.routes:
        for step in route.steps:
            reagents.extend(step.reagents)

    # убираем дубли, сохраняя порядок
    unique_reagents = list(dict.fromkeys(reagents))
    return unique_reagents


def run_pipeline(task: str) -> PipelineResult:
    print("=== Шаг 1: task_parser_agent ===")
    parsed_task = task_parser_agent(task)
    print(parsed_task.model_dump_json(indent=2, ensure_ascii=False))

    print("\n=== Шаг 2: route_agent ===")
    route_result = route_agent(parsed_task)
    print(route_result.model_dump_json(indent=2, ensure_ascii=False))

    print("\n=== Шаг 3: tools / RAG context ===")

    # --- 1. methods retrieval ---
    methods_query = parsed_task.target
    if parsed_task.starting_materials:
        methods_query += " from " + ", ".join(parsed_task.starting_materials)

    methods_result = methods_agent(methods_query)

    print("Methods found:")
    print(methods_result)


    # --- 2. извлечение реагентов из маршрутов ---
    def extract_all_reagents(route_result):
        reagents = []
        for route in route_result.routes:
            for step in route.steps:
                reagents.extend(step.reagents)
        return list(dict.fromkeys(reagents))


    extracted_reagents = extract_all_reagents(route_result)


    # --- 3. reagents retrieval ---
    reagents_result = reagents_agent(extracted_reagents)

    print("Reagents check:")
    print(reagents_result)

    print("\n=== Шаг 4: safety_agent ===")
    safety_result = safety_agent(
            route_result=route_result,
            methods_context=methods_result,
            reagents_context=reagents_result,
        )
    print(safety_result.model_dump_json(indent=2, ensure_ascii=False))

    overall = safety_result.overall_assessment.lower()

    if "low" in overall:
        final_status = "accepted"
    elif "medium" in overall:
        final_status = "review_required"
    elif "high" in overall:
        final_status = "risky"
    else:
        final_status = "unknown"

    return PipelineResult(
        input_task=task,
        parsed_task=parsed_task,
        route=route_result,
        methods_result=methods_result,
        reagents_result=reagents_result,
        safety=safety_result,
        final_status=final_status,
    )


def main():
    task = "Предложи возможные маршруты синтеза аспирина из салициловой кислоты, оцени их безопасность и выбери наиболее безопасный"
    
    # task = input("Введите задачу синтеза: ").strip()
    # if not task:
    #     print("Пустая задача. Завершение.")
    #     return

    print("=== BASELINE ===")
    baseline_result = baseline_agent(task)
    print(baseline_result.model_dump_json(indent=2, ensure_ascii=False))

    print("\n=== MULTI-AGENT PIPELINE ===")
    pipeline_result = run_pipeline(task)

    print("\n=== FINAL PIPELINE RESULT ===")
    print(pipeline_result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()