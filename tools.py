import json
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).resolve().parent
RAG_DIR = BASE_DIR / "rag"
METHODS_PATH = RAG_DIR / "methods.json"
REAGENTS_PATH = RAG_DIR / "reagents.json"


def tool_find_methods(query: str):
    if not METHODS_PATH.exists():
        return {
            "query": query,
            "methods_found": [],
            "best_option": None,
            "message": f"methods file not found: {METHODS_PATH}"
        }

    with open(METHODS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    q = query.lower()
    results = []

    for item in data:
        target_match = item.get("target", "").lower() in q
        synonym_match = any(s.lower() in q for s in item.get("target_synonyms", []))
        starting_match = any(sm.lower() in q for sm in item.get("starting_materials", []))

        if target_match or synonym_match or starting_match:
            results.append(item)

    return {
        "query": query,
        "methods_found": results,
        "best_option": results[0] if results else None,
        "message": "ok" if results else "No methods found"
    }


def _normalize_reagent_name(name: str) -> List[str]:
    n = name.strip().lower()

    replacements = {
        "конц. h2so4 или h3po4 (катализатор)": ["серная кислота", "фосфорная кислота"],
        "h2so4": ["серная кислота"],
        "h3po4": ["фосфорная кислота"],
        "пиридин (связывание hcl)": ["пиридин"],
        "уксусный ангидрид": ["уксусный ангидрид"],
        "ацетилхлорид": ["ацетилхлорид"],
        "салициловая кислота": ["салициловая кислота"],
    }

    for key, value in replacements.items():
        if key in n:
            return value

    if " или " in n:
        return [part.strip() for part in n.split(" или ")]

    return [name.strip()]


def check_reagents(reagents: List[str]):
    if not REAGENTS_PATH.exists():
        return {
            "checked": [],
            "issues": [f"reagents file not found: {REAGENTS_PATH}"]
        }

    with open(REAGENTS_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    expanded_reagents = []
    for r in reagents:
        expanded_reagents.extend(_normalize_reagent_name(r))

    expanded_reagents = list(dict.fromkeys(expanded_reagents))

    results = []
    missing = []

    for r in expanded_reagents:
        r_lower = r.lower()

        found = next(
            (
                item for item in db
                if item.get("name", "").lower() == r_lower
                or r_lower in [s.lower() for s in item.get("synonyms", [])]
            ),
            None
        )

        if found:
            results.append({
                "name": r,
                "available": True,
                "cost": "unknown",
                "hazard": found.get("hazard_level", "unknown"),
                "tags": found.get("hazard_tags", []),
                "description": found.get("description", "")
            })
        else:
            results.append({
                "name": r,
                "available": False,
                "cost": "unknown",
                "hazard": "unknown",
                "tags": []
            })
            missing.append(r)

    return {
        "checked": results,
        "issues": [f"Missing reagents: {', '.join(missing)}"] if missing else []
    }