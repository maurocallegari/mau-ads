#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCHEMA_VERSION = 1
REQUIRED_FILES = ["AGENTS.md", "PROJECT.md", ".ai/project.json"]
VERIFICATION_STATES = {0: "PASS", 1: "FAIL", 2: "UNAVAILABLE", 3: "NOT_RUN", 4: "NOT_APPLICABLE"}
VERIFICATION_PROFILES = {"minimal", "focused", "full", "critical"}


class ContractError(RuntimeError):
    pass


def load_manifest(root: Path) -> dict:
    path = root / ".ai" / "project.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError("missing .ai/project.json") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid .ai/project.json: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError(".ai/project.json must contain a JSON object")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ContractError(f"schema_version must be {SCHEMA_VERSION}")
    if data.get("profile") != "generic":
        raise ContractError("profile must be 'generic'")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        raise ContractError("name must be a non-empty string")
    return data


def verification_path(root: Path, manifest: dict) -> Path:
    verification = manifest.get("verification")
    if not isinstance(verification, dict):
        raise ContractError("verification must be an object")
    command = verification.get("command")
    if not isinstance(command, str) or not command.strip():
        raise ContractError("verification.command must be a non-empty repository-local path")
    parts = command.split()
    if len(parts) != 1:
        raise ContractError("verification.command must reference one repository-local entry point")
    raw = Path(parts[0])
    if raw.is_absolute() or ".." in raw.parts:
        raise ContractError("verification.command must stay inside the repository")
    path = (root / raw).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ContractError("verification.command escapes the repository") from exc
    return path


def validate(
    repository: str | Path,
    run_verification: bool = False,
    verification_profile: str | None = None,
) -> dict:
    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise ContractError(f"not a directory: {root}")
    if verification_profile is not None and verification_profile not in VERIFICATION_PROFILES:
        raise ContractError(f"unknown verification profile: {verification_profile}")

    missing = [item for item in REQUIRED_FILES if not (root / item).is_file()]
    if missing:
        raise ContractError("missing required files: " + ", ".join(missing))

    manifest = load_manifest(root)
    verify = verification_path(root, manifest)
    if not verify.is_file():
        raise ContractError(f"verification entry point not found: {verify.relative_to(root)}")

    result = {
        "schema_version": SCHEMA_VERSION,
        "kind": "mau.contract_validation",
        "repository": str(root),
        "contract": "PASS",
        "verification": "NOT_RUN",
        "verification_command": verify.relative_to(root).as_posix(),
        "verification_profile": verification_profile,
    }

    if run_verification:
        command = ["bash", str(verify)] if verify.suffix == ".sh" else [str(verify)]
        env = os.environ.copy()
        if verification_profile:
            env["MAU_VERIFICATION_PROFILE"] = verification_profile
        completed = subprocess.run(command, cwd=root, check=False, env=env)
        result["verification"] = VERIFICATION_STATES.get(completed.returncode, "FAIL")
        result["verification_exit_code"] = completed.returncode
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the MAU ADS project contract")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--run-verification", action="store_true")
    parser.add_argument("--verification-profile", choices=sorted(VERIFICATION_PROFILES))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        payload = validate(args.repository, args.run_verification, args.verification_profile)
    except ContractError as exc:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "kind": "mau.contract_validation",
            "contract": "FAIL",
            "verification": "NOT_RUN",
            "error": str(exc),
        }
        if args.json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print("PASS: repository contract")
        if args.run_verification:
            suffix = f" ({args.verification_profile})" if args.verification_profile else ""
            print(f"{payload['verification']}: project verification{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
