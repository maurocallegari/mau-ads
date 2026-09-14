#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from onboarding.validate_project import ContractError, load_manifest, validate, verification_path
from runtime.analyze_repository import analyze

SCHEMA_VERSION = 1
STATE_RELATIVE_PATH = Path(".ai/onboarding.json")
RESOLVED = "RESOLVED"
UNRESOLVED = "UNRESOLVED"
OPEN = "OPEN"
ANSWERED = "ANSWERED"


class OnboardingGateError(RuntimeError):
    pass


def _root(repository: str | Path) -> Path:
    return Path(analyze(repository)["repository"]["root"])


def _state_path(root: Path) -> Path:
    return root / STATE_RELATIVE_PATH


def _read_state(root: Path) -> dict:
    path = _state_path(root)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OnboardingGateError(f"missing {STATE_RELATIVE_PATH.as_posix()}") from exc
    except json.JSONDecodeError as exc:
        raise OnboardingGateError(f"invalid {STATE_RELATIVE_PATH.as_posix()}: {exc}") from exc
    if not isinstance(payload, dict):
        raise OnboardingGateError(f"{STATE_RELATIVE_PATH.as_posix()} must contain a JSON object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise OnboardingGateError(f"onboarding schema_version must be {SCHEMA_VERSION}")
    if payload.get("kind") != "mau.onboarding_state":
        raise OnboardingGateError("onboarding kind must be 'mau.onboarding_state'")
    return payload


def _evidence_ready(section: object) -> bool:
    if not isinstance(section, dict):
        return False
    evidence = section.get("evidence")
    return isinstance(evidence, list) and any(str(item).strip() for item in evidence)


def _open_questions(state: dict) -> list[dict]:
    questions = state.get("questions", [])
    if not isinstance(questions, list):
        raise OnboardingGateError("onboarding questions must be an array")
    result: list[dict] = []
    for question in questions:
        if not isinstance(question, dict):
            raise OnboardingGateError("each onboarding question must be an object")
        if question.get("status") == OPEN:
            result.append(question)
    return result


def initial_state(repository: str | Path, verification_command: str = "dev/verify-local.sh") -> dict:
    analysis = analyze(repository)
    root = Path(analysis["repository"]["root"])
    git = analysis["repository"]["git"]
    observed = analysis["evidence"]
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "mau.onboarding_state",
        "status": "NEEDS_ASSESSMENT",
        "repository": {
            "name": analysis["repository"]["name"],
            "origin": git.get("origin"),
            "observed_root": str(root),
            "structure_fingerprint": analysis["structure"]["fingerprint"],
        },
        "purpose": {
            "status": UNRESOLVED,
            "summary": None,
            "evidence": [],
        },
        "canonical_source": {
            "status": UNRESOLVED,
            "path": None,
            "evidence": [],
        },
        "constraints": [],
        "verification": {
            "status": UNRESOLVED,
            "command": verification_command,
            "baseline": "NOT_RUN",
            "verifier_sha256": None,
            "evidence": [],
        },
        "observed_evidence": {
            "manifests": observed.get("manifests", []),
            "ci": observed.get("ci", []),
            "tests": observed.get("tests", [])[:50],
            "migrations_or_schema": observed.get("migrations_or_schema", [])[:50],
            "entrypoint_candidates": observed.get("entrypoint_candidates", [])[:50],
        },
        "questions": [],
        "instructions": [
            "Inspect repository evidence before asking the user.",
            "Resolve purpose and canonical source from repository evidence when possible.",
            "If a functional, ownership, environment or safety fact cannot be resolved, add an OPEN question instead of guessing.",
            "Replace the generated UNAVAILABLE verifier with project-owned checks before finalizing onboarding.",
            "Run onboarding_gate.py finalize only after the assessment is complete.",
        ],
    }


def seed(repository: str | Path) -> dict:
    root = _root(repository)
    path = _state_path(root)
    if path.exists():
        return {"status": "EXISTS", "path": str(path), "state": _read_state(root)}
    path.parent.mkdir(parents=True, exist_ok=True)
    state = initial_state(root)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return {"status": "CREATED", "path": str(path), "state": state}


def _verifier_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(repository: str | Path) -> dict:
    root = _root(repository)
    path = _state_path(root)
    if not path.is_file():
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_gate",
            "status": "NEEDS_ASSESSMENT",
            "repository": str(root),
            "user_input_required": False,
            "reason": f"missing {STATE_RELATIVE_PATH.as_posix()}",
            "actions": [{"type": "seed_onboarding_state"}, {"type": "assess_repository"}],
        }

    try:
        state = _read_state(root)
        questions = _open_questions(state)
    except OnboardingGateError as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_gate",
            "status": "BLOCKED",
            "repository": str(root),
            "user_input_required": False,
            "reason": str(exc),
            "actions": [{"type": "repair_onboarding_state"}],
        }

    if questions:
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_gate",
            "status": "NEEDS_CLARIFICATION",
            "repository": str(root),
            "user_input_required": True,
            "open_questions": questions,
            "reason": "onboarding has unresolved questions that require human input",
            "actions": [
                {"type": "ask_user", "questions": questions},
                {"type": "record_onboarding_answers", "path": STATE_RELATIVE_PATH.as_posix()},
                {"type": "rerun_onboarding_gate"},
            ],
        }

    purpose = state.get("purpose")
    canonical = state.get("canonical_source")
    unresolved: list[str] = []
    if not isinstance(purpose, dict) or purpose.get("status") != RESOLVED or not str(purpose.get("summary") or "").strip() or not _evidence_ready(purpose):
        unresolved.append("purpose")
    if not isinstance(canonical, dict) or canonical.get("status") != RESOLVED or not str(canonical.get("path") or "").strip() or not _evidence_ready(canonical):
        unresolved.append("canonical_source")

    if unresolved:
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_gate",
            "status": "NEEDS_ASSESSMENT",
            "repository": str(root),
            "user_input_required": False,
            "unresolved": unresolved,
            "reason": "repository assessment is incomplete; inspect evidence before asking the user",
            "actions": [{"type": "assess_repository", "path": STATE_RELATIVE_PATH.as_posix(), "unresolved": unresolved}],
        }

    source_path = (root / str(canonical["path"])).resolve()
    try:
        source_path.relative_to(root.resolve())
    except ValueError:
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_gate",
            "status": "BLOCKED",
            "repository": str(root),
            "user_input_required": False,
            "reason": "canonical_source.path escapes repository root",
            "actions": [{"type": "repair_onboarding_state"}],
        }
    if not source_path.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_gate",
            "status": "BLOCKED",
            "repository": str(root),
            "user_input_required": False,
            "reason": f"canonical source path does not exist: {canonical['path']}",
            "actions": [{"type": "repair_onboarding_state"}],
        }

    try:
        manifest = load_manifest(root)
        verifier = verification_path(root, manifest)
    except ContractError as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_gate",
            "status": "BLOCKED",
            "repository": str(root),
            "user_input_required": False,
            "reason": str(exc),
            "actions": [{"type": "repair_project_contract"}],
        }

    verification = state.get("verification")
    if not isinstance(verification, dict):
        verification = {}
    command = manifest["verification"]["command"]
    command_matches = verification.get("command") == command
    verifier_exists = verifier.is_file()
    verifier_hash = _verifier_sha256(verifier) if verifier_exists else None
    verified = (
        verification.get("status") == "VERIFIED"
        and verification.get("baseline") == "PASS"
        and command_matches
        and verifier_exists
        and verification.get("verifier_sha256") == verifier_hash
        and _evidence_ready(verification)
    )
    if not verified:
        reasons: list[str] = []
        if not command_matches:
            reasons.append("onboarding verification command differs from .ai/project.json")
        if not verifier_exists:
            reasons.append("verification entry point is missing")
        if verification.get("baseline") != "PASS":
            reasons.append("verification baseline has not passed")
        if verifier_exists and verification.get("verifier_sha256") and verification.get("verifier_sha256") != verifier_hash:
            reasons.append("verification entry point changed after onboarding baseline")
        if not _evidence_ready(verification):
            reasons.append("verification evidence is missing")
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_gate",
            "status": "NEEDS_VERIFICATION_SETUP",
            "repository": str(root),
            "user_input_required": False,
            "verification_command": command,
            "reason": "; ".join(reasons) or "project verification is not finalized",
            "actions": [
                {"type": "configure_project_verifier", "command": command},
                {"type": "finalize_onboarding", "verification_profile": "focused"},
            ],
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "mau.onboarding_gate",
        "status": "READY",
        "repository": str(root),
        "user_input_required": False,
        "purpose": purpose.get("summary"),
        "canonical_source": canonical.get("path"),
        "verification_command": command,
        "verification_baseline": "PASS",
    }


def finalize(repository: str | Path) -> dict:
    root = _root(repository)
    state = _read_state(root)
    questions = _open_questions(state)
    if questions:
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_finalize",
            "status": "BLOCKED",
            "reason": "open onboarding questions remain",
            "open_questions": questions,
        }

    purpose = state.get("purpose")
    canonical = state.get("canonical_source")
    if not isinstance(purpose, dict) or purpose.get("status") != RESOLVED or not str(purpose.get("summary") or "").strip() or not _evidence_ready(purpose):
        return {"schema_version": SCHEMA_VERSION, "kind": "mau.onboarding_finalize", "status": "BLOCKED", "reason": "purpose is not resolved with evidence"}
    if not isinstance(canonical, dict) or canonical.get("status") != RESOLVED or not str(canonical.get("path") or "").strip() or not _evidence_ready(canonical):
        return {"schema_version": SCHEMA_VERSION, "kind": "mau.onboarding_finalize", "status": "BLOCKED", "reason": "canonical source is not resolved with evidence"}

    source_path = (root / str(canonical["path"])).resolve()
    try:
        source_path.relative_to(root.resolve())
    except ValueError:
        return {"schema_version": SCHEMA_VERSION, "kind": "mau.onboarding_finalize", "status": "BLOCKED", "reason": "canonical source escapes repository root"}
    if not source_path.exists():
        return {"schema_version": SCHEMA_VERSION, "kind": "mau.onboarding_finalize", "status": "BLOCKED", "reason": "canonical source path does not exist"}

    try:
        contract = validate(root, run_verification=True, verification_profile="focused")
        manifest = load_manifest(root)
        verifier = verification_path(root, manifest)
    except ContractError as exc:
        return {"schema_version": SCHEMA_VERSION, "kind": "mau.onboarding_finalize", "status": "BLOCKED", "reason": str(exc)}

    if contract.get("verification") != "PASS":
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.onboarding_finalize",
            "status": "BLOCKED",
            "verification": contract.get("verification"),
            "reason": "focused project verification must PASS before onboarding is READY",
        }

    state["status"] = "READY"
    state["verification"] = {
        "status": "VERIFIED",
        "command": manifest["verification"]["command"],
        "baseline": "PASS",
        "profile": "focused",
        "verifier_sha256": _verifier_sha256(verifier),
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "evidence": [
            f"project verifier exited PASS with MAU_VERIFICATION_PROFILE=focused",
            f"sha256:{_verifier_sha256(verifier)}",
        ],
    }
    state["repository"]["structure_fingerprint"] = analyze(root)["structure"]["fingerprint"]
    _state_path(root).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    result = evaluate(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "mau.onboarding_finalize",
        "status": result["status"],
        "verification": "PASS",
        "gate": result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic MAU ADS onboarding readiness gate")
    parser.add_argument("command", choices=("status", "seed", "finalize"))
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    if args.command == "seed":
        payload = seed(args.repository)
        exit_code = 0
    elif args.command == "finalize":
        payload = finalize(args.repository)
        exit_code = 0 if payload.get("status") == "READY" else 2
    else:
        payload = evaluate(args.repository)
        exit_code = 0 if payload.get("status") == "READY" else 2

    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
