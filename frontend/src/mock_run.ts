export function generateMockRun(query: string) {
  const normalized = query.toLowerCase().trim();

  const isErrorCase = normalized.includes("ошибка");
  const isPlanCase = normalized.includes("план");

  let finalAnswer =
    "Запрос обработан. Рекомендую уточнить задачу и критерии результата.";

  if (isPlanCase) {
    finalAnswer =
      "План действий: 1) определить цель, 2) разбить задачу на шаги, 3) проверить результат валидатором.";
  }

  if (isErrorCase) {
    finalAnswer =
      "Обнаружена ошибка во входных данных. Уточни постановку задачи и повтори запрос.";
  }

  return {
    status: "completed",
    route: {
      status: "completed",
      selected_path: isErrorCase ? "validator_agent" : "method_agent",
      reasoning: isErrorCase
        ? "Route направил запрос в Validator, потому что обнаружен риск ошибки."
        : "Route направил запрос в Method Agent для построения решения.",
    },
    validator: {
      status: "completed",
      is_valid: !isErrorCase,
      comment: isErrorCase
        ? "Найдены проблемы, требуется доработка входных данных."
        : "Проверка пройдена успешно.",
    },
    result: {
      final_answer: finalAnswer,
    },
  };
}