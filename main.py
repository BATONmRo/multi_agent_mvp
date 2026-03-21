from agents import route_agent, validator_agent


def main():
    target = "Получить вещество X (или просто тестовая задача)"

    print("=== Шаг 1: route_agent ===")
    route_result = route_agent(target)
    print(route_result.model_dump_json(indent=2, ensure_ascii=False))

    print("\n=== Шаг 2: validator_agent ===")
    validation_result = validator_agent(route_result)
    print(validation_result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()