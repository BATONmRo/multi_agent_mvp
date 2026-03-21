from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ----------------------------
# Route generation schemas
# ----------------------------

class RouteStep(BaseModel):
    reaction: str = Field(..., description="Название реакции или типа превращения")
    reagents: List[str] = Field(default_factory=list, description="Список реагентов")
    conditions: str = Field(..., description="Условия проведения шага")


class RouteCandidate(BaseModel):
    id: str = Field(..., description="Уникальный идентификатор маршрута")
    summary: str = Field(..., description="Краткое описание маршрута")
    steps: List[RouteStep] = Field(default_factory=list, description="Шаги маршрута")


class RouteAgentOutput(BaseModel):
    target: str = Field(..., description="Целевое соединение")
    routes: List[RouteCandidate] = Field(default_factory=list, description="Список кандидатов маршрутов")
    route_count: int = Field(..., description="Количество маршрутов")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность модели")


# ----------------------------
# Task parser schemas
# ----------------------------

class TaskParserOutput(BaseModel):
    task_type: Literal["single_route_assessment", "multi_route_ranking"] = Field(
        ...,
        description="Тип задачи для оркестратора"
    )
    original_task: str = Field(..., description="Исходный запрос пользователя")
    target: str = Field(..., description="Целевое соединение или цель синтеза")
    starting_materials: List[str] = Field(
        default_factory=list,
        description="Исходные вещества, если указаны"
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Ограничения или предпочтения пользователя"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность parser-агента")


# ----------------------------
# Safety schemas
# ----------------------------

class HazardousComponent(BaseModel):
    name: str = Field(..., description="Название опасного компонента")
    risk: str = Field(..., description="Краткое описание риска")


class RouteSafetyAssessment(BaseModel):
    route_id: str = Field(..., description="ID маршрута")
    risk_level: Literal["low", "medium", "high", "unknown"] = Field(
        ...,
        description="Уровень риска маршрута"
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Числовая оценка риска, больше = опаснее"
    )
    hazardous_components: List[HazardousComponent] = Field(
        default_factory=list,
        description="Опасные реагенты/компоненты"
    )
    process_risks: List[str] = Field(
        default_factory=list,
        description="Риски процесса"
    )
    justification: str = Field(..., description="Краткое объяснение оценки")


class SafetyAssessmentOutput(BaseModel):
    target: str = Field(..., description="Целевое соединение")
    overall_assessment: str = Field(..., description="Общая оценка по задаче")
    recommended_route_id: Optional[str] = Field(
        default=None,
        description="Предпочтительный маршрут по безопасности"
    )
    route_assessments: List[RouteSafetyAssessment] = Field(
        default_factory=list,
        description="Оценки по каждому маршруту"
    )


# ----------------------------
# Baseline schemas
# ----------------------------

class BaselineOutput(BaseModel):
    task: str = Field(..., description="Исходная задача")
    answer: str = Field(..., description="Ответ baseline-модели")


# ----------------------------
# Final pipeline schema
# ----------------------------

class PipelineResult(BaseModel):
    input_task: str = Field(..., description="Исходный запрос пользователя")
    parsed_task: TaskParserOutput = Field(..., description="Результат parser-агента")
    route: RouteAgentOutput = Field(..., description="Результат route-агента")
    methods_result: Dict[str, Any] = Field(
        default_factory=dict,
        description="Контекст/результаты поиска методов"
    )
    reagents_result: Dict[str, Any] = Field(
        default_factory=dict,
        description="Проверка реагентов"
    )
    safety: SafetyAssessmentOutput = Field(..., description="Результат safety-агента")
    final_status: str = Field(..., description="Итоговый статус пайплайна")