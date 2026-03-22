import json
from pprint import pprint

from agents import (
    task_parser_agent,
    route_agent,
    safety_agent,
    baseline_agent,
    methods_agent,
    reagents_agent,
    run_judge,
)
from schemas import PipelineResult
from llm import client

SHOW_PIPELINE_LOGS = False


def pretty_print(title: str, data) -> None:
    print(f"\n=== {title} ===")

    try:
        if hasattr(data, "model_dump"):
            data = data.model_dump()

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                print(data)
                return

        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        pprint(data, sort_dicts=False)


def extract_all_reagents(route_result) -> list[str]:
    reagents = []

    for route in route_result.routes:
        for step in route.steps:
            reagents.extend(step.reagents)

    return list(dict.fromkeys(reagents))


def render_pipeline_answer(pipeline_result: PipelineResult) -> str:
    lines = []

    parsed = pipeline_result.parsed_task
    route_result = pipeline_result.route
    safety = pipeline_result.safety
    methods_result = pipeline_result.methods_result
    reagents_result = pipeline_result.reagents_result

    lines.append(f"Задача: {parsed.original_task}")
    lines.append("")

    if parsed.starting_materials:
        lines.append("Исходные вещества:")
        for sm in parsed.starting_materials:
            lines.append(f"• {sm}")
        lines.append("")

    lines.append("Найденные маршруты:")
    for i, route in enumerate(route_result.routes, start=1):
        lines.append(f"{i}. {route.summary}")
        for step_idx, step in enumerate(route.steps, start=1):
            lines.append(f"   Этап {step_idx}: {step.reaction}")
            if step.reagents:
                lines.append(f"   Реагенты: {', '.join(step.reagents)}")
            if step.conditions:
                lines.append(f"   Условия: {step.conditions}")
        lines.append("")

    lines.append("Оценка безопасности маршрутов:")
    for ra in safety.route_assessments:
        lines.append(f"- {ra.route_id}: риск = {ra.risk_level}, score = {ra.score}")

        if ra.hazardous_components:
            lines.append("  Опасные компоненты:")
            for comp in ra.hazardous_components:
                if isinstance(comp, dict):
                    name = comp.get("name", "unknown")
                    risk = comp.get("risk", "unknown")
                    lines.append(f"  • {name}: {risk}")
                else:
                    lines.append(f"  • {comp}")

        if ra.process_risks:
            lines.append("  Риски процесса:")
            for risk in ra.process_risks:
                lines.append(f"  • {risk}")

        if ra.justification:
            lines.append(f"  Обоснование: {ra.justification}")

        lines.append("")

    best_route_id = safety.recommended_route_id
    lines.append(f"Рекомендуемый маршрут: {best_route_id}")

    best_route = next((r for r in route_result.routes if r.id == best_route_id), None)
    if best_route is not None:
        lines.append(f"Наиболее безопасный вариант: {best_route.summary}")

    lines.append("")
    lines.append(f"Общая оценка: {safety.overall_assessment}")
    lines.append("")

    if isinstance(reagents_result, dict) and reagents_result.get("issues"):
        lines.append("Замечания по реагентам:")
        for issue in reagents_result["issues"]:
            lines.append(f"• {issue}")
        lines.append("")

    if isinstance(methods_result, dict) and methods_result.get("best_option"):
        best_option = methods_result["best_option"]
        lines.append("Подтверждение из RAG:")
        lines.append(f"• Лучший найденный метод: {best_option.get('title', 'unknown')}")

        advantages = best_option.get("advantages", [])
        disadvantages = best_option.get("disadvantages", [])

        if advantages:
            lines.append("• Преимущества:")
            for a in advantages:
                lines.append(f"  - {a}")

        if disadvantages:
            lines.append("• Ограничения:")
            for d in disadvantages:
                lines.append(f"  - {d}")

    return "\n".join(lines)


def run_pipeline(task: str) -> PipelineResult:
    parsed_task = task_parser_agent(task)
    if SHOW_PIPELINE_LOGS:
        pretty_print("Шаг 1: task_parser_agent", parsed_task)

    route_result = route_agent(parsed_task)
    if SHOW_PIPELINE_LOGS:
        pretty_print("Шаг 2: route_agent", route_result)

    methods_query = parsed_task.target
    if parsed_task.starting_materials:
        methods_query += " from " + ", ".join(parsed_task.starting_materials)

    methods_result = methods_agent(methods_query)
    if SHOW_PIPELINE_LOGS:
        pretty_print("Шаг 3a: methods_agent / RAG context", methods_result)

    extracted_reagents = extract_all_reagents(route_result)
    if SHOW_PIPELINE_LOGS:
        pretty_print("Извлечённые реагенты", extracted_reagents)

    reagents_result = reagents_agent(extracted_reagents)
    if SHOW_PIPELINE_LOGS:
        pretty_print("Шаг 3b: reagents_agent", reagents_result)

    safety_result = safety_agent(
        route_result=route_result,
        methods_context=methods_result,
        reagents_context=reagents_result,
    )
    if SHOW_PIPELINE_LOGS:
        pretty_print("Шаг 4: safety_agent", safety_result)

    overall = str(safety_result.overall_assessment).lower()

    if "low" in overall or "низ" in overall:
        final_status = "accepted"
    elif "medium" in overall or "сред" in overall:
        final_status = "review_required"
    elif "high" in overall or "высок" in overall or "опас" in overall:
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

    task = input("Введите задачу синтеза: ").strip()
    if not task:
       print("Пустая задача. Завершение.")
       return

    print("=== BASELINE ===")
    baseline_result = baseline_agent(task)
    print(f"task: {baseline_result.task}\n")
    print("answer:")
    print(baseline_result.answer)

    pipeline_result = run_pipeline(task)
    mas_text = render_pipeline_answer(pipeline_result)

    print("\n=== MAS ANSWER ===")
    print(mas_text)

    print("\n=== JUDGE EVALUATION ===")
    judge_result = run_judge(
        llm_client=client,
        task=task,
        baseline_answer=baseline_result.answer,
        mas_answer=mas_text,
        reference_context=""
    )
    pretty_print("JUDGE RESULT", judge_result)


if __name__ == "__main__":
    main()