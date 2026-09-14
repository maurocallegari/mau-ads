from __future__ import annotations


def route(request: str) -> dict:
    text = request.casefold()
    risk = "NORMAL"
    reasons: list[str] = []

    critical = (
        "production", "deploy", "delete data", "drop table", "credential", "secret",
        "rotate key", "irreversible",
    )
    elevated = (
        "auth", "permission", "migration", "schema", "database", "payment", "billing",
        "shared core", "external side effect",
    )

    if any(signal in text for signal in critical):
        risk = "CRITICAL"
        reasons.append("request contains critical-operation signal")
    elif any(signal in text for signal in elevated):
        risk = "ELEVATED"
        reasons.append("request contains elevated-risk signal")

    capabilities: list[str] = []
    if any(signal in text for signal in ("bug", "fix", "erro", "broken", "regression", "non funziona", "doesn't work", "does not work")):
        capabilities.append("bug-investigation")
    if any(signal in text for signal in ("feature", "add ", "aggiung", "implement", "nuova funzione", "new function")):
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
        "risk": {"level": risk, "reasons": reasons},
        "capabilities": capabilities,
    }
