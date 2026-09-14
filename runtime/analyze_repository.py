#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = 1
MAX_FILES = 10000
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", "node_modules", "vendor",
    "dist", "build", "target", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", "coverage", ".coverage", ".next", ".cache",
}
MANIFEST_NAMES = {
    "package.json", "pyproject.toml", "requirements.txt", "Pipfile", "composer.json",
    "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile",
    "mix.exs", "Dockerfile", "Makefile",
}
CONFIG_NAMES = {
    ".env.example", ".env.sample", ".env.template", "docker-compose.yml",
    "docker-compose.yaml", "compose.yml", "compose.yaml",
}
CONTEXT_NAMES = {
    "AGENTS.md", "PROJECT.md", "REPO_MAP.md", "CLAUDE.md", ".cursorrules", "CONTRIBUTING.md",
}
ENTRYPOINT_NAMES = {
    "main.py", "app.py", "server.py", "index.js", "index.ts", "main.js", "main.ts",
    "main.go", "main.rs", "index.html", "manage.py",
}
TEST_DIR_NAMES = {"test", "tests", "spec", "specs", "__tests__"}
MIGRATION_DIR_NAMES = {"migration", "migrations", "schema", "schemas"}


def _run_git(root: Path, *args: str) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
            check=False,
            timeout=8,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 127, ""
    return completed.returncode, completed.stdout.strip()


def repository_root(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    code, out = _run_git(resolved, "rev-parse", "--show-toplevel")
    return Path(out).resolve() if code == 0 and out else resolved


def iter_files(root: Path) -> Iterable[Path]:
    count = 0
    for current, dirs, names in os.walk(root):
        current_path = Path(current)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(names):
            path = current_path / name
            try:
                rel = path.relative_to(root)
            except ValueError:
                continue
            yield rel
            count += 1
            if count >= MAX_FILES:
                return


def analyze(path: str | Path) -> dict:
    root = repository_root(Path(path))
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")

    files = list(iter_files(root))
    file_strings = [p.as_posix() for p in files]
    top_level = sorted({p.parts[0] for p in files if p.parts})
    manifests = sorted(p.as_posix() for p in files if p.name in MANIFEST_NAMES)
    configs = sorted(p.as_posix() for p in files if p.name in CONFIG_NAMES)
    contexts = sorted(p.as_posix() for p in files if p.name in CONTEXT_NAMES)
    entrypoints = sorted(p.as_posix() for p in files if p.name in ENTRYPOINT_NAMES)
    tests = sorted(
        p.as_posix()
        for p in files
        if any(part.lower() in TEST_DIR_NAMES for part in p.parts[:-1])
        or p.name.lower().startswith(("test_", "spec_"))
        or p.name.lower().endswith(("_test.py", ".test.js", ".test.ts", ".spec.js", ".spec.ts"))
    )
    migrations = sorted(
        p.as_posix()
        for p in files
        if any(part.lower() in MIGRATION_DIR_NAMES for part in p.parts[:-1])
    )
    ci = sorted(
        p.as_posix()
        for p in files
        if (
            len(p.parts) >= 3
            and p.parts[0] == ".github"
            and p.parts[1] == "workflows"
            and p.suffix.lower() in {".yml", ".yaml"}
        )
        or p.as_posix() in {"Jenkinsfile", ".gitlab-ci.yml"}
    )

    _, branch = _run_git(root, "branch", "--show-current")
    _, head = _run_git(root, "rev-parse", "HEAD")
    _, remote = _run_git(root, "remote", "get-url", "origin")
    status_code, status = _run_git(root, "status", "--porcelain")
    missing = [item for item in ["AGENTS.md", "PROJECT.md", ".ai/project.json"] if item not in file_strings]

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "mau.repository_analysis",
        "repository": {
            "root": str(root),
            "name": root.name,
            "git": {
                "available": bool(head),
                "branch": branch or None,
                "head": head or None,
                "origin": remote or None,
                "dirty": bool(status) if status_code == 0 else None,
            },
        },
        "structure": {
            "file_count_scanned": len(files),
            "scan_truncated": len(files) >= MAX_FILES,
            "top_level": top_level,
            "fingerprint": hashlib.sha256("\n".join(file_strings).encode()).hexdigest(),
        },
        "contract": {
            "ready_shape": not missing,
            "missing": missing,
            "present_context": contexts,
        },
        "evidence": {
            "manifests": manifests,
            "configuration_examples": configs,
            "ci": ci,
            "tests": tests[:200],
            "migrations_or_schema": migrations[:200],
            "entrypoint_candidates": entrypoints[:100],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect read-only MAU ADS repository evidence")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        payload = analyze(args.repository)
    except ValueError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}))
        return 1
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
