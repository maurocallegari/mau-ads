from __future__ import annotations


TRIVIAL_SIGNALS = (
    "label",
    "etichetta",
    "typo",
    "refuso",
    "copy text",
    "testo",
    "rename",
    "rinomina",
    "placeholder",
    "tooltip",
)

COMPLEX_SIGNALS = (
    "new section",
    "nuova sezione",
    "new module",
    "nuovo modulo",
    "new feature",
    "nuova funzione",
    "workflow",
    "integration",
    "integrazione",
    "migration",
    "schema",
    "database",
    "auth",
    "permission",
    "permesso",
    "shared core",
    "api",
    "background job",
    "cron",
)


def _risk(text: str) -> tuple[str, list[str]]:
    risk = "NORMAL"
    reasons: list[str] = []

    critical = (
        "production",
        "deploy",
        "delete data",
        "drop table",
        "credential",
        "secret",
        "rotate key",
        "irreversible",
    )
    elevated = (
        "auth",
        "permission",
        "migration",
        "schema",
        "database",
        "payment",
        "billing",
        "shared core",
        "external side effect",
    )

    if any(signal in text for signal in critical):
        risk = "CRITICAL"
        reasons.append("request contains critical-operation signal")
    elif any(signal in text for signal in elevated):
        risk = "ELEVATED"
        reasons.append("request contains elevated-risk signal")

    return risk, reasons


def _complexity(text: str, risk: str) -> tuple[str, list[str]]:
    reasons: list[str] = []

    if risk == "CRITICAL":
        return "COMPLEX", ["critical risk requires full workflow"]

    if any(signal in text for signal in COMPLEX_SIGNALS):
        reasons.append("request contains cross-cutting or structural signal")
        return "COMPLEX", reasons

    if risk == "ELEVATED":
        reasons.append("elevated risk prevents trivial routing")
        return "STANDARD", reasons

    if any(signal in text for signal in TRIVIAL_SIGNALS):
        reasons.append("request appears local and deterministic")
        return "TRIVIAL", reasons

    return "STANDARD", reasons


def _workflow(risk: str, complexity: str) -> dict:
    if risk == "CRITICAL":
        return {
            "engine": "spec-kit",
            "profile": "critical",
            "sequence": [
                "speckit.specify",
                "speckit.clarify",
                "speckit.plan",
                "speckit.checklist",
                "speckit.tasks",
                "speckit.analyze",
                "speckit.implement",
                "speckit.converge",
            ],
        }

    if complexity == "COMPLEX":
        return {
            "engine": "spec-kit",
            "profile": "full",
            "sequence": [
                "speckit.specify",
                "speckit.clarify",
                "speckit.plan",
                "speckit.tasks",
                "speckit.analyze",
                "speckit.implement",
                "speckit.converge",
            ],
        }

    if complexity == "STANDARD":
        return {
            "engine": "spec-kit",
            "profile": "standard",
            "sequence": [
                "speckit.specify",
                "speckit.plan",
                "speckit.tasks",
                "speckit.implement",
                "speckit.converge",
            ],
        }

    return {
        "engine": "direct",
        "profile": "trivial",
        "sequence": ["inspect", "implement", "verify"],
    }


def _verification(risk: str, complexity: str) -> dict:
    if risk == "CRITICAL":
        return {"profile": "critical", "minimum": ["project", "targeted", "integration", "diff-review"]}
    if complexity == "COMPLEX":
        return {"profile": "full", "minimum": ["project", "targeted", "integration", "diff-review"]}
    if complexity == "STANDARD":
        return {"profile": "focused", "minimum": ["project", "targeted", "diff-review"]}
    return {"profile": "minimal", "minimum": ["targeted", "diff-review"]}


def _model_policy(risk: str, complexity: str) -> dict:
    """Return cost/capability tiers, never vendor-specific model names."""
    if risk == "CRITICAL":
        return {"analysis": "strong", "implementation": "strong", "verification": "balanced"}
    if complexity == "COMPLEX":
        return {"analysis": "strong", "implementation": "balanced", "verification": "economy"}
    if complexity == "STANDARD":
        return {"analysis": "balanced", "implementation": "economy", "verification": "economy"}
    return {"analysis": "economy", "implementation": "economy", "verification": "economy"}


def route(request: str) -> dict:
    text = request.casefold()
    risk, risk_reasons = _risk(text)
    complexity, complexity_reasons = _complexity(text, risk)

    capabilities: list[str] = []
    if any(signal in text for signal in ("bug", "fix", "erro", "broken", "regression", "non funziona", "doesn't work", "does not work")):
        capabilities.append("bug-investigation")
    if any(signal in text for signal in ("feature", "add ", "aggiung", "implement", "nuova funzione", "new function", "new section", "nuova sezione")):
        capabilities.append("feature-planning")
    if any(signal in text for signal in ("ui", "ux", "frontend", "layout", "mobile", "responsive", "css", "design", "browser")):
        capabilities.append("interface-verification")
    if any(signal in text for signal in ("migration", "schema", "database", "data", "record", "table")):
        capabilities.append("persistent-data-safety")
    if not capabilities:
        capabilities.append("code-change")
    if "code-review" not in capabilities:
        capabilities.append("code-review")

    return {
        "risk": {"level": risk, "reasons": risk_reasons},
        "complexity": {"level": complexity, "reasons": complexity_reasons},
        "workflow": _workflow(risk, complexity),
        "verification": _verification(risk, complexity),
        "model_policy": _model_policy(risk, complexity),
        "capabilities": capabilities,
    }
