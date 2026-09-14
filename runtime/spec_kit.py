#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def _run(command: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout)


def status(repository: str | Path) -> dict:
    root = Path(repository).expanduser().resolve()
    executable = shutil.which("specify")
    initialized = (root / ".specify").is_dir()
    integration_file = root / ".specify" / "integration.json"
    integration = None
    if integration_file.is_file():
        try:
            payload = json.loads(integration_file.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                integration = payload.get("default_integration") or payload.get("integration")
        except json.JSONDecodeError:
            integration = None

    if not executable:
        state = "UNAVAILABLE"
        reason = "Spec Kit CLI is not installed"
    elif not initialized:
        state = "NEEDS_INIT"
        reason = "repository is not initialized for Spec Kit"
    else:
        state = "READY"
        reason = None

    return {
        "schema_version": 1,
        "kind": "mau.spec_kit_status",
        "status": state,
        "repository": str(root),
        "cli": executable,
        "initialized": initialized,
        "integration": integration,
        "reason": reason,
    }


def initialize(
    repository: str | Path,
    integration: str = "codex",
    script: str = "py",
    lean: bool = True,
) -> dict:
    root = Path(repository).expanduser().resolve()
    executable = shutil.which("specify")
    if not executable:
        return {
            "schema_version": 1,
            "kind": "mau.spec_kit_init",
            "status": "UNAVAILABLE",
            "repository": str(root),
            "reason": "Spec Kit CLI is not installed",
        }

    command = [
        executable,
        "init",
        "--here",
        "--force",
        "--non-interactive",
        "--integration",
        integration,
        "--script",
        script,
        "--ignore-agent-tools",
    ]
    if lean:
        command.extend(("--preset", "lean"))

    initialized = _run(command, root)
    if initialized.returncode != 0:
        return {
            "schema_version": 1,
            "kind": "mau.spec_kit_init",
            "status": "BLOCKED",
            "repository": str(root),
            "command": command[1:],
            "stdout": initialized.stdout[-4000:],
            "stderr": initialized.stderr[-4000:],
            "reason": "specify init failed",
        }

    current = status(root)
    return {
        "schema_version": 1,
        "kind": "mau.spec_kit_init",
        "status": "READY" if current["status"] == "READY" else "BLOCKED",
        "repository": str(root),
        "integration": integration,
        "script": script,
        "preset": "lean" if lean else None,
        "current": current,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="MAU adapter for GitHub Spec Kit")
    parser.add_argument("--pretty", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("status")
    check.add_argument("repository", nargs="?", default=".")

    init = sub.add_parser("init")
    init.add_argument("repository", nargs="?", default=".")
    init.add_argument("--integration", default="codex")
    init.add_argument("--script", choices=("sh", "ps", "py"), default="py")
    init.add_argument("--no-lean", action="store_true")

    args = parser.parse_args()

    if args.command == "status":
        payload = status(args.repository)
        ok = payload["status"] == "READY"
    else:
        payload = initialize(args.repository, args.integration, args.script, not args.no_lean)
        ok = payload["status"] == "READY"

    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
