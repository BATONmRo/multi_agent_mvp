# import json
# from pathlib import Path


# BASE_DIR = Path(__file__).resolve().parent
# METHODS_PATH = BASE_DIR / "rag" / "methods.json"

# with open(METHODS_PATH, "r", encoding="utf-8") as f:
#     METHODS = json.load(f)


# def _score_method(query: str, method: dict) -> int:
#     query_words = query.lower().split()

#     searchable_text = " ".join(
#         [
#             method.get("reaction", ""),
#             method.get("conditions", ""),
#             " ".join(method.get("substrates", [])),
#             " ".join(method.get("reagents", [])),
#         ]
#     ).lower()

#     score = 0
#     for word in query_words:
#         if word in searchable_text:
#             score += 1

#     if query.lower() in method.get("reaction", "").lower():
#         score += 3

#     return score


# def search_methods(query: str, top_k: int = 3) -> list[dict]:
#     scored = []

#     for method in METHODS:
#         score = _score_method(query, method)
#         if score > 0:
#             scored.append((score, method))

#     scored.sort(key=lambda x: x[0], reverse=True)
#     return [item[1] for item in scored[:top_k]]