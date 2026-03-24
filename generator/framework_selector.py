"""
Framework Selection Engine.

Analyzes project characteristics and recommends the best REST framework.
"""


def select_framework(
    characteristics: dict,
    functions: list[dict],
    classes: list[dict],
    files: dict[str, str],
) -> tuple[str, str]:
    """
    Choose the best framework and explain why.

    Returns: (framework_name, reasoning)
    """
    has_async    = characteristics.get("has_async", False)
    has_db       = characteristics.get("has_db_models", False)
    has_ml       = characteristics.get("has_ml_models", False)
    has_file_io  = characteristics.get("has_file_io", False)
    num_funcs    = len(functions)
    num_classes  = len(classes)

    # ── Multi-Language Overrides ──
    has_java = any(f.endswith(".java") for f in files.keys())
    has_js = any(f.endswith(".js") for f in files.keys())
    has_ts = any(f.endswith(".ts") for f in files.keys())
    has_go = any(f.endswith(".go") for f in files.keys())
    has_cs = any(f.endswith(".cs") for f in files.keys())

    if has_cs:
        return "asp_net", "Recommended ASP.NET Core because the source code contains C# files."
    if has_java:
        return "spring_boot", "Recommended Spring Boot because the source code contains Java files."
    if has_go:
        return "gin", "Recommended Gin because the source code contains Go files."
    if has_ts:
        return "express_ts", "Recommended Node.js (Express with TypeScript) because the source code contains TypeScript files."
    if has_js:
        return "express", "Recommended Node.js (Express) because the source code contains JavaScript files."

    scores = {
        "fastapi": 0,
        "flask": 0,
        "django": 0,
        "serverless": 0,
    }
    reasons = {
        "fastapi": [],
        "flask": [],
        "django": [],
        "serverless": [],
    }

    # ── Async code → FastAPI excels ──
    if has_async:
        scores["fastapi"] += 30
        reasons["fastapi"].append("native async/await support")

    # ── ML models → FastAPI (async, type hints, high performance) ──
    if has_ml:
        scores["fastapi"] += 25
        reasons["fastapi"].append("ideal for ML model serving with auto-docs and async support")
        scores["serverless"] += 10
        reasons["serverless"].append("can serve ML models as serverless functions")

    # ── DB models → Django (ORM, admin) or FastAPI (SQLAlchemy) ──
    if has_db:
        scores["django"] += 25
        reasons["django"].append("excellent ORM and admin panel for database-heavy apps")
        scores["fastapi"] += 15
        reasons["fastapi"].append("works great with SQLAlchemy for database operations")

    # ── File I/O → FastAPI (UploadFile) ──
    if has_file_io:
        scores["fastapi"] += 15
        reasons["fastapi"].append("built-in UploadFile handling for file operations")
        scores["flask"] += 10
        reasons["flask"].append("straightforward file upload handling")

    # ── Project size considerations ──
    if num_funcs <= 3 and num_classes <= 1:
        scores["serverless"] += 20
        reasons["serverless"].append("small codebase ideal for serverless deployment")
        scores["flask"] += 15
        reasons["flask"].append("lightweight and simple for small projects")

    if num_funcs > 10 or num_classes > 5:
        scores["django"] += 15
        reasons["django"].append("structured framework for large, complex projects")
        scores["fastapi"] += 10
        reasons["fastapi"].append("modular router system scales well for large projects")

    # ── Always give FastAPI and Flask baseline points ──
    scores["fastapi"] += 20  # modern default
    reasons["fastapi"].append("modern Python API framework with auto-generated OpenAPI docs")
    scores["flask"] += 10
    reasons["flask"].append("mature ecosystem with extensive community support")

    # Pick the winner
    best_framework = max(scores, key=scores.get)
    best_reasons = reasons[best_framework]

    # Build explanation
    framework_display = {
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django REST Framework",
        "serverless": "Serverless (AWS Lambda / Cloud Functions)",
    }

    reason_text = (
        f"Recommended {framework_display[best_framework]} because: "
        + "; ".join(best_reasons)
        + f". (Score: {scores[best_framework]} — "
        + " vs ".join(f"{framework_display[k]}: {v}" for k, v in sorted(scores.items(), key=lambda x: -x[1]))
        + ")"
    )

    return best_framework, reason_text
