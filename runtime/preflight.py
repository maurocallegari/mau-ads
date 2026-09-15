#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from onboarding.validate_project import ContractError, load_manifest, validate
from runtime.analyze_repository import analyze

ALLOWED_ENV_SUFFIXES = (".example", ".sample", ".template")


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=20)


def _check(status: str, name: str, evidence: str) -> dict:
    return {"name": name, "status": status, "evidence": evidence}


def _tracked_secret_candidates(root: Path) -> list[str]:
    completed = _run(["git", "ls-files"], root)
    if completed.returncode != 0:
        return []
    bad: list[str] = []
    for raw in completed.stdout.splitlines():
        name = Path(raw).name
        if name == ".env" or name.startswith(".env."):
            if name.endswith(ALLOWED_ENV_SUFFIXES):
                continue
            bad.append(raw)
        if name in {"id_rsa", "id_ed25519"} or name.endswith((".pem", ".p12", ".pfx")):
            bad.append(raw)
    return sorted(set(bad))


def _is_ignored(root: Path, relative: str) -> bool:
    return _run(["git", "check-ignore", "-q", "--no-index", relative], root).returncode == 0


def preflight(repository: str | Path, phase: str = "intake", base: str = "main") -> dict:
    root = Path(repository).expanduser().resolve()
    checks: list[dict] = []

    try:
        contract = validate(root, run_verification=False)
        checks.append(_check("PASS", "CONTRACT", "repository contract validates"))
        manifest = load_manifest(root)
    except ContractError as exc:
        checks.append(_check("FAIL", "CONTRACT", str(exc)))
        return {"schema_version": 1, "kind": "mau.preflight", "phase": phase, "status": "BLOCKED", "checks": checks}

    analysis = analyze(root)
    git = analysis["repository"]["git"]
    if git["available"]:
        checks.append(_check("PASS", "GIT_REPOSITORY", f"HEAD {git['head']}"))
    else:
        checks.append(_check("FAIL", "GIT_REPOSITORY", "Git HEAD unavailable"))

    branch = git.get("branch")
    if branch and branch != base:
        checks.append(_check("PASS", "ISOLATED_BRANCH", branch))
    else:
        checks.append(_check("FAIL", "ISOLATED_BRANCH", f"expected non-{base} branch, observed {branch or 'none'}"))

    secret_candidates = _tracked_secret_candidates(root)
    if secret_candidates:
        checks.append(_check("FAIL", "SECRETS_EXCLUDED", "tracked sensitive files: " + ", ".join(secret_candidates)))
    else:
        checks.append(_check("PASS", "SECRETS_EXCLUDED", "no tracked runtime env/private-key candidates detected"))

    production = (manifest.get("environments") or {}).get("production") or {}
    if production.get("deployment_authorization", "explicit") == "explicit":
        checks.append(_check("PASS", "PRODUCTION_BOUNDARY", "production deployment requires explicit authorization"))
    else:
        checks.append(_check("FAIL", "PRODUCTION_BOUNDARY", "production deployment authorization is not explicit"))

    if manifest["profile"] == "mauro-php":
        required = ["configure.php", "require/ads.php", ".env.example"]
        missing = [item for item in required if not (root / item).is_file()]
        if missing:
            status = "PENDING" if phase == "intake" else "FAIL"
            checks.append(_check(status, "CONFIG_BOUNDARY", "missing: " + ", ".join(missing)))
        else:
            checks.append(_check("PASS", "CONFIG_BOUNDARY", "configure.php, require/ads.php and .env.example present"))

        if (root / ".env").exists() and _is_ignored(root, ".env"):
            checks.append(_check("PASS", "LOCAL_RUNTIME_ENV", ".env exists and is ignored"))
        elif phase == "intake":
            checks.append(_check("PENDING", "LOCAL_RUNTIME_ENV", ".env not yet available in isolated workspace"))
        else:
            checks.append(_check("FAIL", "LOCAL_RUNTIME_ENV", ".env must exist locally and remain ignored"))

    blockers = [item for item in checks if item["status"] == "FAIL"]
    status = "BLOCKED" if blockers else "PASS"
    return {
        "schema_version": 1,
        "kind": "mau.preflight",
        "phase": phase,
        "profile": contract.get("profile"),
        "status": status,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic MAU ADS preflight checks")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--phase", choices=("intake", "completion"), default="intake")
    parser.add_argument("--base", default="main")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = preflight(args.repository, args.phase, args.base)
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
