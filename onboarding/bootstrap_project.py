#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from onboarding.onboarding_gate import initial_state
from runtime.analyze_repository import analyze

AGENTS_TEMPLATE = """# AGENTS.md

## MAU ADS gate

Before any durable edit, obtain a valid MAU work context. The user does not need to run MAU commands. A compatible worker or orchestrator invokes the gate automatically.

No valid work context means no durable writes.

If repository onboarding is not `READY`, only onboarding reconciliation is allowed. Inspect repository evidence first; ask the user only for facts that cannot be resolved safely from the repository. Do not edit application code until onboarding and task-level gates authorize implementation.

## Before editing

- Read `.ai/project.json`, `.ai/onboarding.json`, `PROJECT.md` and `REPO_MAP.md` when present.
- Inspect relevant source and tests before changing behavior.
- Preserve repository evidence over remembered session assumptions.

## Verification

- Run the repository-owned verification entry point before completion.
- Report `PASS`, `FAIL`, `UNAVAILABLE`, `NOT_RUN`, or `NOT_APPLICABLE` truthfully.
- Inspect the final diff for unintended edits.

## Safety

- Never commit secrets.
- Do not use production as a development workspace.
- Production deployment requires explicit authorization.
"""

VERIFY_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

echo "MAU verification is not configured for this repository." >&2
echo "Replace this file with project-owned checks before claiming PASS." >&2
exit 2
"""


def _project_text(data: dict) -> str:
    evidence = data["evidence"]
    return f"""# Project

## Purpose

Purpose was not safely inferable from deterministic evidence. Repository onboarding must resolve this from source/docs or ask the user before implementation is authorized.

## Repository evidence

- observed manifests: {', '.join(evidence['manifests']) or 'none'}
- observed CI: {', '.join(evidence['ci']) or 'none'}
- observed test evidence: {len(evidence['tests'])} path(s)
- observed migration/schema evidence: {len(evidence['migrations_or_schema'])} path(s)

## Onboarding

Machine-readable onboarding evidence lives in `.ai/onboarding.json`. This document may be enriched from repository evidence once onboarding has converged.

## Verification

The canonical local verification entry point is declared in `.ai/project.json`.
A generated `UNAVAILABLE` verifier is not a PASS and must be replaced with real project checks before onboarding can become `READY`.
"""


def _repo_map_text(data: dict) -> str:
    rows = [
        f"| `{item}` | observed top-level path; inspect before assigning a more specific role |"
        for item in data["structure"]["top_level"][:40]
    ]
    return "# Repository map\n\n| Path | Observed role |\n|---|---|\n" + ("\n".join(rows) if rows else "| `.` | repository root |") + "\n"


def bootstrap(repository: str | Path) -> dict:
    data = analyze(repository)
    root = Path(data["repository"]["root"])
    created: list[str] = []

    targets = [
        (root / "AGENTS.md", AGENTS_TEMPLATE),
        (root / "PROJECT.md", _project_text(data)),
        (root / "REPO_MAP.md", _repo_map_text(data)),
        (
            root / ".ai" / "project.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "profile": "generic",
                    "name": root.name,
                    "verification": {"command": "dev/verify-local.sh"},
                },
                indent=2,
            ) + "\n",
        ),
        (
            root / ".ai" / "onboarding.json",
            json.dumps(initial_state(root), indent=2) + "\n",
        ),
        (root / "dev" / "verify-local.sh", VERIFY_TEMPLATE),
    ]

    for path, content in targets:
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if path.name == "verify-local.sh":
            path.chmod(path.stat().st_mode | 0o111)
        created.append(path.relative_to(root).as_posix())

    return {
        "schema_version": 2,
        "kind": "mau.onboarding_bootstrap",
        "repository": str(root),
        "created": created,
        "preserved_existing": True,
        "onboarding_status": "NEEDS_ASSESSMENT",
        "implementation_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely bootstrap the MAU ADS project contract")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(bootstrap(args.repository), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
