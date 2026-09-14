from __future__ import annotations


TRIVIAL_SIGNALS = (
    "label",
    "etichetta",
    "typo",
    "refuso",
    "copy text",
    "testo del pulsante",
    "testo etichetta",
    "rename label",
    "rinomina etichetta",
    "placeholder",
    "tooltip",
)

TRIVIAL_DISQUALIFIERS = (
    "add ",
    "aggiung",
    "implement",
    "create ",
    "crea ",
    "new ",
    "nuov",
    "module",
    "modulo",
    "section",
    "sezione",
    "workflow",
    "integration",
    "integrazione",
    "database",
    "schema",
    "migration",
    "auth",
    "permission",
    "permesso",
    "api",
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


def _trivial_request_is_self_contained(text: str) -> bool:
    """Keep the direct path only for explicit, deterministic replacements."""
    if "->" in text or "→" in text:
        return True

    replacement_pairs = (
        (" da ", " a "),
        (" from ", " to "),
    )
    for start, end in replacement_pairs:
        start_at = text.find(start)
        if start_at < 0:
            continue
        end_at = text.find(end, start_at + len(start))
        if end_at > start_at + len(start) and text[end_at + len(end):].strip():
            return True
    return False


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

    looks_trivial = any(signal in text for signal in TRIVIAL_SIGNALS)
    has_disqualifier = any(signal in text for signal in TRIVIAL_DISQUALIFIERS)
    if looks_trivial and not has_disqualifier and _trivial_request_is_self_contained(text):
        reasons.append("request is explicitly local, self-contained and deterministic")
        return "TRIVIAL", reasons

    if looks_trivial and not has_disqualifier:
        reasons.append("apparently small request is not self-contained; clarification path required")

    # Unknown or under-specified work deliberately falls upward. The router may
    # over-verify an ambiguous request, but it must not under-classify it as trivial.
    return "STANDARD", reasons


def _workflow(risk: str, complexity: str) -> dict:
    if risk == "CRITICAL":
        return {
            "engine": "spec-kit",
            "profile": "critical",
            "sequence": [
                "speckit.specify",
                "speckit.clarify",
                "mau.clarification-gate",
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
                "mau.clarification-gate",
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
                "speckit.clarify",
                "mau.clarification-gate",
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
