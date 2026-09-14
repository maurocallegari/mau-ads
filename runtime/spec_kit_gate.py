#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


PROFILES = {"trivial", "standard", "full", "critical"}
UNCHECKED = re.compile(r"^\s*-\s*\[\s\]\s+", re.MULTILINE)
CLARIFICATION_STATUSES = {"CLEAR", "NEEDS_USER"}
QUESTION_CATEGORIES = {"technical", "functional", "risk", "irreversible"}


class SpecKitGateError(RuntimeError):
    pass


def _inside(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise SpecKitGateError("active Spec Kit feature escapes repository root") from exc
    return resolved


def active_feature_dir(repository: str | Path) -> Path:
    root = Path(repository).expanduser().resolve()
    explicit = os.environ.get("SPECIFY_FEATURE_DIRECTORY")
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_absolute():
            candidate = root / candidate
        path = _inside(root, candidate)
    else:
        pointer = root / ".specify" / "feature.json"
        try:
            payload = json.loads(pointer.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise SpecKitGateError("missing .specify/feature.json; no active Spec Kit feature") from exc
        except json.JSONDecodeError as exc:
            raise SpecKitGateError(f"invalid .specify/feature.json: {exc}") from exc
        feature_directory = payload.get("feature_directory") if isinstance(payload, dict) else None
        if not isinstance(feature_directory, str) or not feature_directory.strip():
            raise SpecKitGateError(".specify/feature.json has no feature_directory")
        candidate = Path(feature_directory)
        if not candidate.is_absolute():
            candidate = root / candidate
        path = _inside(root, candidate)

    if not path.is_dir():
        raise SpecKitGateError(f"active Spec Kit feature directory does not exist: {path}")
    return path


def _unchecked(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if UNCHECKED.match(line)]


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def clarification_state(repository: str | Path) -> dict:
    """Validate the pre-implementation clarification artifact.

    Semantic assessment is produced by the primary worker after Spec Kit specify/
    clarify. This function makes the result mechanically enforceable: unresolved
    functional/risk decisions block implementation, while only sourced technical
    assumptions are allowed.
    """
    root = Path(repository).expanduser().resolve()
    try:
        feature = active_feature_dir(root)
    except SpecKitGateError as exc:
        return {
            "schema_version": 1,
            "kind": "mau.clarification_gate",
            "status": "NOT_ASSESSED",
            "repository": str(root),
            "reason": str(exc),
        }

    artifact = feature / "clarification.json"
    if not artifact.is_file():
        return {
            "schema_version": 1,
            "kind": "mau.clarification_gate",
            "status": "NOT_ASSESSED",
            "repository": str(root),
            "feature_directory": str(feature),
            "artifact": str(artifact),
            "reason": "missing clarification.json; requirements have not been mechanically assessed",
        }

    try:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "schema_version": 1,
            "kind": "mau.clarification_gate",
            "status": "BLOCKED",
            "repository": str(root),
            "feature_directory": str(feature),
            "artifact": str(artifact),
            "reason": f"invalid clarification.json: {exc}",
        }

    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        return {
            "schema_version": 1,
            "kind": "mau.clarification_gate",
            "status": "BLOCKED",
            "repository": str(root),
            "feature_directory": str(feature),
            "artifact": str(artifact),
            "reason": "clarification.json must be an object with schema_version 1",
        }

    declared = payload.get("status")
    if declared not in CLARIFICATION_STATUSES:
        return {
            "schema_version": 1,
            "kind": "mau.clarification_gate",
            "status": "BLOCKED",
            "repository": str(root),
            "feature_directory": str(feature),
            "artifact": str(artifact),
            "reason": "clarification status must be CLEAR or NEEDS_USER",
        }

    questions = payload.get("questions", [])
    assumptions = payload.get("assumptions", [])
    if not isinstance(questions, list) or not isinstance(assumptions, list):
        return {
            "schema_version": 1,
            "kind": "mau.clarification_gate",
            "status": "BLOCKED",
            "repository": str(root),
            "feature_directory": str(feature),
            "artifact": str(artifact),
            "reason": "questions and assumptions must be arrays",
        }

    open_questions: list[dict] = []
    resolved_questions: list[dict] = []
    seen_ids: set[str] = set()
    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            return {
                "schema_version": 1,
                "kind": "mau.clarification_gate",
                "status": "BLOCKED",
                "repository": str(root),
                "feature_directory": str(feature),
                "artifact": str(artifact),
                "reason": f"question {index} must be an object",
            }
        qid = _text(question.get("id"))
        wording = _text(question.get("question"))
        category = question.get("category")
        if not qid or qid in seen_ids or not wording or category not in QUESTION_CATEGORIES:
            return {
                "schema_version": 1,
                "kind": "mau.clarification_gate",
                "status": "BLOCKED",
                "repository": str(root),
                "feature_directory": str(feature),
                "artifact": str(artifact),
                "reason": f"question {index} needs a unique id, wording and valid category",
            }
        seen_ids.add(qid)
        normalized = {
            "id": qid,
            "question": wording,
            "category": category,
            "answer": _text(question.get("answer")),
            "source": _text(question.get("source")),
        }
        if normalized["answer"] or normalized["source"]:
            resolved_questions.append(normalized)
        else:
            open_questions.append(normalized)

    for index, assumption in enumerate(assumptions, start=1):
        if not isinstance(assumption, dict):
            return {
                "schema_version": 1,
                "kind": "mau.clarification_gate",
                "status": "BLOCKED",
                "repository": str(root),
                "feature_directory": str(feature),
                "artifact": str(artifact),
                "reason": f"assumption {index} must be an object",
            }
        category = assumption.get("category")
        text = _text(assumption.get("text"))
        source = _text(assumption.get("source"))
        if category != "technical" or not text or not source:
            return {
                "schema_version": 1,
                "kind": "mau.clarification_gate",
                "status": "BLOCKED",
                "repository": str(root),
                "feature_directory": str(feature),
                "artifact": str(artifact),
                "reason": "only sourced technical assumptions are allowed; functional/risk/irreversible decisions must be resolved as questions",
            }

    base = {
        "schema_version": 1,
        "kind": "mau.clarification_gate",
        "repository": str(root),
        "feature_directory": str(feature),
        "artifact": str(artifact),
        "declared_status": declared,
        "open_questions": open_questions,
        "resolved_questions": resolved_questions,
        "assumption_count": len(assumptions),
    }

    if open_questions:
        if declared != "NEEDS_USER":
            return {
                **base,
                "status": "BLOCKED",
                "reason": "clarification declares CLEAR while unresolved questions remain",
            }
        return {
            **base,
            "status": "NEEDS_USER",
            "reason": "user decisions are required before implementation",
        }

    if declared != "CLEAR":
        return {
            **base,
            "status": "BLOCKED",
            "reason": "clarification declares NEEDS_USER but no unresolved questions remain",
        }

    return {
        **base,
        "status": "PASS",
        "reason": "requirements are sufficiently resolved for implementation",
    }


def verify(repository: str | Path, profile: str) -> dict:
    if profile not in PROFILES:
        raise SpecKitGateError(f"unknown Spec Kit profile: {profile}")

    root = Path(repository).expanduser().resolve()
    if profile == "trivial":
        return {
            "schema_version": 1,
            "kind": "mau.spec_kit_gate",
            "profile": profile,
            "status": "NOT_APPLICABLE",
            "repository": str(root),
            "reason": "trivial work does not require Spec Kit artifacts",
        }

    if not (root / ".specify").is_dir():
        return {
            "schema_version": 1,
            "kind": "mau.spec_kit_gate",
            "profile": profile,
            "status": "BLOCKED",
            "repository": str(root),
            "reason": "Spec Kit is not initialized in the repository",
        }

    try:
        feature = active_feature_dir(root)
    except SpecKitGateError as exc:
        return {
            "schema_version": 1,
            "kind": "mau.spec_kit_gate",
            "profile": profile,
            "status": "BLOCKED",
            "repository": str(root),
            "reason": str(exc),
        }

    clarification = clarification_state(root)
    if clarification["status"] != "PASS":
        return {
            "schema_version": 1,
            "kind": "mau.spec_kit_gate",
            "profile": profile,
            "status": "BLOCKED",
            "repository": str(root),
            "feature_directory": str(feature),
            "clarification": clarification,
            "reason": "pre-implementation clarification gate did not pass",
        }

    required = ["spec.md", "plan.md", "tasks.md"]
    missing = [name for name in required if not (feature / name).is_file()]
    if missing:
        return {
            "schema_version": 1,
            "kind": "mau.spec_kit_gate",
            "profile": profile,
            "status": "BLOCKED",
            "repository": str(root),
            "feature_directory": str(feature),
            "clarification": clarification,
            "missing": missing,
            "reason": "required Spec Kit artifacts are missing",
        }

    open_tasks = _unchecked(feature / "tasks.md")
    if open_tasks:
        return {
            "schema_version": 1,
            "kind": "mau.spec_kit_gate",
            "profile": profile,
            "status": "BLOCKED",
            "repository": str(root),
            "feature_directory": str(feature),
            "clarification": clarification,
            "open_tasks": open_tasks[:50],
            "reason": "tasks.md still contains incomplete implementation tasks",
        }

    checklist_open: list[str] = []
    checklist_dir = feature / "checklists"
    if checklist_dir.is_dir():
        for path in sorted(checklist_dir.glob("*.md")):
            checklist_open.extend(f"{path.name}: {item}" for item in _unchecked(path))

    if profile == "critical" and checklist_open:
        return {
            "schema_version": 1,
            "kind": "mau.spec_kit_gate",
            "profile": profile,
            "status": "BLOCKED",
            "repository": str(root),
            "feature_directory": str(feature),
            "clarification": clarification,
            "open_checklist_items": checklist_open[:50],
            "reason": "critical workflow has incomplete checklist items",
        }

    return {
        "schema_version": 1,
        "kind": "mau.spec_kit_gate",
        "profile": profile,
        "status": "PASS",
        "repository": str(root),
        "feature_directory": str(feature),
        "clarification": clarification,
        "artifacts": required,
        "open_checklist_items": checklist_open[:50],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify MAU-required Spec Kit artifacts")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    parser.add_argument("--clarification-only", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    try:
        payload = clarification_state(args.repository) if args.clarification_only else verify(args.repository, args.profile)
    except SpecKitGateError as exc:
        payload = {
            "schema_version": 1,
            "kind": "mau.spec_kit_gate",
            "profile": args.profile,
            "status": "BLOCKED",
            "reason": str(exc),
        }

    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    ok = {"PASS", "NOT_APPLICABLE"}
    return 0 if payload["status"] in ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
