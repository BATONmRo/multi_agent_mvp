import json
from pathlib import Path
from retrieval import search_methods


BASE_DIR = Path(__file__).resolve().parent
REAGENTS_PATH = BASE_DIR / "data" / "reagents.json"

with open(REAGENTS_PATH, "r", encoding="utf-8") as f:
    REAGENTS = json.load(f)


def tool_find_methods(query: str) -> dict:
    results = search_methods(query)

    if not results:
        return {
            "query": query,
            "methods_found": [],
            "best_option": None,
            "message": "No methods found"
        }

    best_option = results[0]["reaction"]

    return {
        "query": query,
        "methods_found": results,
        "best_option": best_option,
        "message": "Methods retrieved successfully"
    }


def check_reagents(reagent_list: list[str]) -> dict:
    checked = []
    missing = []
    risky = []

    for reagent in reagent_list:
        found = next(
            (r for r in REAGENTS if r["name"].lower() == reagent.lower()),
            None
        )

        if found:
            item = {
                "name": found["name"],
                "available": found["available"],
                "cost": found["cost"],
                "hazard": found["hazard"]
            }
            checked.append(item)

            if not found["available"]:
                missing.append(found["name"])

            if found["hazard"] == "high":
                risky.append(found["name"])
        else:
            checked.append({
                "name": reagent,
                "available": False,
                "cost": "unknown",
                "hazard": "unknown"
            })
            missing.append(reagent)

    issues = []
    if missing:
        issues.append(f"Missing reagents: {', '.join(missing)}")
    if risky:
        issues.append(f"High-hazard reagents: {', '.join(risky)}")

    return {
        "checked": checked,
        "issues": issues if issues else ["No critical issues"]
    }