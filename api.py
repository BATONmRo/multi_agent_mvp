from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import run_pipeline
from agents import baseline_agent


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/run")
def run_endpoint(data: RunRequest):
    task = data.query

    pipeline_result = run_pipeline(task)
    baseline_result = baseline_agent(task)

    return {
        "status": "completed",
        "task_parser": {
            "task_type": pipeline_result.parsed_task.task_type,
            "target": pipeline_result.parsed_task.target,
            "starting_materials": pipeline_result.parsed_task.starting_materials,
            "confidence": pipeline_result.parsed_task.confidence,
        },
        "route": {
            "target": pipeline_result.route.target,
            "route_count": pipeline_result.route.route_count,
            "confidence": pipeline_result.route.confidence,
            "routes": [
                {
                    "id": route.id,
                    "summary": route.summary,
                }
                for route in pipeline_result.route.routes
            ],
        },
        "methods": pipeline_result.methods_result,
        "reagents": pipeline_result.reagents_result,
        "safety": pipeline_result.safety.model_dump(),
        "baseline": baseline_result.model_dump(),
        "result": {
            "final_answer": (
                f"Для цели '{pipeline_result.parsed_task.target}' "
                f"рекомендован маршрут '{pipeline_result.safety.recommended_route_id}' "
                f"со статусом '{pipeline_result.final_status}'."
            )
        },
    }