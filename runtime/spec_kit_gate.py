#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


PROFILES = {"trivial", "standard", "full", "critical"}
UNCHECKED = re.compile(r"^\s*-\s*\[\s\]\s+", re.MULTILINE)


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
        "artifacts": required,
        "open_checklist_items": checklist_open[:50],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify MAU-required Spec Kit artifacts")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    try:
        payload = verify(args.repository, args.profile)
    except SpecKitGateError as exc:
        payload = {
            "schema_version": 1,
            "kind": "mau.spec_kit_gate",
            "profile": args.profile,
            "status": "BLOCKED",
            "reason": str(exc),
        }

    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["status"] in {"PASS", "NOT_APPLICABLE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
