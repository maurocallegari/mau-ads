#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from onboarding.bootstrap_project import bootstrap
from onboarding.validate_project import ContractError, validate
from runtime.analyze_repository import analyze
from runtime.routing import route
from runtime.spec_kit import status as spec_kit_status


def _run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=20)


def _slug(text: str, limit: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug or "work")[:limit].rstrip("-")


def _github_repo_from_origin(origin: str | None) -> str | None:
    if not origin:
        return None
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$", origin)
    return f"{match.group(1)}/{match.group(2)}" if match else None


def _resolve_or_create_issue(root: Path, request: str, origin: str | None) -> dict:
    repo = _github_repo_from_origin(origin)
    if not repo:
        return {"status": "UNAVAILABLE", "reason": "origin is not a recognized GitHub repository"}
    if not shutil.which("gh"):
        return {"status": "UNAVAILABLE", "reason": "GitHub CLI is unavailable", "repository": repo}

    auth = _run(["gh", "auth", "status"], cwd=root)
    if auth.returncode != 0:
        return {"status": "UNAVAILABLE", "reason": "GitHub CLI is not authenticated", "repository": repo}

    title = request.strip().splitlines()[0][:120]
    search = _run(
        [
            "gh", "issue", "list", "--repo", repo, "--state", "open", "--search",
            f'"{title}" in:title', "--json", "number,title,url", "--limit", "20",
        ],
        cwd=root,
    )
    if search.returncode == 0:
        try:
            matches = json.loads(search.stdout or "[]")
        except json.JSONDecodeError:
            matches = []
        for item in matches:
            if str(item.get("title", "")).strip().casefold() == title.casefold():
                return {"status": "READY", "source": "existing", **item, "repository": repo}

    body = "Created automatically by the MAU ADS standalone intake gate.\n\nRequested outcome:\n\n" + request.strip() + "\n"
    created = _run(["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body], cwd=root)
    if created.returncode != 0:
        return {"status": "UNAVAILABLE", "reason": created.stderr.strip() or "issue creation failed", "repository": repo}
    url = created.stdout.strip().splitlines()[-1]
    number_match = re.search(r"/issues/(\d+)$", url)
    return {
        "status": "READY",
        "source": "created",
        "number": int(number_match.group(1)) if number_match else None,
        "title": title,
        "url": url,
        "repository": repo,
    }


def _prepare_worktree(root: Path, issue: dict, request: str) -> dict:
    if issue.get("status") != "READY" or not issue.get("number"):
        return {"status": "BLOCKED", "reason": "canonical GitHub Issue is not ready"}

    analysis = analyze(root)
    if analysis["repository"]["git"]["dirty"]:
        return {"status": "BLOCKED", "reason": "source working tree is dirty"}

    issue_number = int(issue["number"])
    branch = f"mau/issue-{issue_number}-{_slug(request)}"
    worktree_root = root.parent / ".mau-worktrees"
    path = worktree_root / f"{root.name}-issue-{issue_number}"

    existing = _run(["git", "-C", str(root), "branch", "--list", branch])
    branch_exists = bool(existing.stdout.strip())
    if path.exists():
        return {"status": "READY", "branch": branch, "path": str(path), "source": "existing-path"}

    worktree_root.mkdir(parents=True, exist_ok=True)
    command = ["git", "-C", str(root), "worktree", "add", str(path)]
    command += [branch] if branch_exists else ["-b", branch, "HEAD"]
    created = _run(command)
    if created.returncode != 0:
        return {"status": "BLOCKED", "reason": created.stderr.strip() or "worktree creation failed"}
    return {"status": "READY", "branch": branch, "path": str(path), "source": "created"}


def _execution_contract(routing: dict, work: dict) -> dict:
    workflow = routing["workflow"]
    verification = routing["verification"]
    workspace = work.get("path") if work.get("status") == "READY" else None
    requires_spec_kit = workflow["engine"] == "spec-kit"
    kit = spec_kit_status(workspace) if requires_spec_kit and workspace else None

    actions: list[dict] = []
    if requires_spec_kit and kit and kit.get("status") == "NEEDS_INIT":
        actions.append(
            {
                "type": "initialize_spec_kit",
                "workspace": workspace,
                "integration": "codex",
                "script": "py",
                "preset": "lean",
            }
        )
    if requires_spec_kit and kit and kit.get("status") == "UNAVAILABLE":
        actions.extend(
            [
                {
                    "type": "install_spec_kit_cli",
                    "reason": kit.get("reason"),
                },
                {
                    "type": "initialize_spec_kit",
                    "workspace": workspace,
                    "integration": "codex",
                    "script": "py",
                    "preset": "lean",
                    "after": "install_spec_kit_cli",
                },
            ]
        )

    execution_ready = not requires_spec_kit or bool(kit and kit.get("status") == "READY")
    actions.append(
        {
            "type": "complete_work",
            "workspace": workspace,
            "workflow_profile": workflow["profile"],
            "verification_profile": verification["profile"],
        }
    )

    return {
        "status": "READY" if execution_ready else "NEEDS_RECONCILE",
        "engine": workflow["engine"],
        "workflow_profile": workflow["profile"],
        "required_sequence": workflow["sequence"],
        "verification_profile": verification["profile"],
        "verification_minimum": verification["minimum"],
        "model_policy": routing["model_policy"],
        "spec_kit_required": requires_spec_kit,
        "spec_kit": kit,
        "actions": actions,
    }


def intake(
    repository: str | Path,
    request: str,
    mode: str = "standalone",
    bootstrap_missing: bool = True,
    issue_number: int | None = None,
    workspace: str | None = None,
    prepare_workspace: bool = True,
) -> dict:
    initial = analyze(repository)
    root = Path(initial["repository"]["root"])
    onboarding_result = None

    try:
        contract = validate(root, False)
    except ContractError:
        if not bootstrap_missing:
            contract = {"contract": "FAIL", "verification": "NOT_RUN"}
        else:
            onboarding_result = bootstrap(root)
            contract = validate(root, False)

    analysis = analyze(root)
    routing = route(request)

    if mode == "standalone":
        issue = {"status": "READY", "source": "provided", "number": issue_number} if issue_number else _resolve_or_create_issue(root, request, analysis["repository"]["git"]["origin"])
        work = _prepare_worktree(root, issue, request) if prepare_workspace else {"status": "NOT_RUN", "reason": "workspace preparation disabled"}
        write_authorized = contract.get("contract") == "PASS" and issue.get("status") == "READY" and work.get("status") == "READY"
        delegated: list[str] = []
    else:
        issue = {"status": "READY" if issue_number else "REQUIRED", "source": "orchestrator", "number": issue_number}
        work = {"status": "READY" if workspace else "REQUIRED", "source": "orchestrator", "path": workspace}
        write_authorized = contract.get("contract") == "PASS" and bool(issue_number) and bool(workspace)
        delegated = ["work_item", "workspace_isolation", "worker_dispatch", "github_delivery"]

    execution = _execution_contract(routing, work)
    implementation_authorized = write_authorized and execution["status"] == "READY"

    return {
        "schema_version": 2,
        "kind": "mau.work_context",
        "mode": mode,
        "request": request,
        "repository": {
            "root": str(root),
            "fingerprint": analysis["structure"]["fingerprint"],
            "contract": contract["contract"],
        },
        "onboarding": onboarding_result,
        "work_item": issue,
        "workspace": work,
        "routing": routing,
        "execution": execution,
        "delegated_to_orchestrator": delegated,
        "write_authorized": write_authorized,
        "implementation_authorized": implementation_authorized,
        "gate_reconciliation_authorized": write_authorized and not implementation_authorized,
        "completion_requires": {
            "workflow_artifacts": execution["spec_kit_required"],
            "project_verification": True,
            "verification_profile": execution["verification_profile"],
            "final_diff_review": True,
            "truthful_verification_state": True,
            "production_authorization_separate": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Automatic MAU ADS machine-facing intake gate")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--request", required=True)
    parser.add_argument("--mode", choices=("standalone", "external-orchestrator"), default="standalone")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--workspace")
    parser.add_argument("--no-bootstrap", action="store_true")
    parser.add_argument("--no-workspace", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = intake(
        args.repository,
        args.request,
        args.mode,
        not args.no_bootstrap,
        args.issue,
        args.workspace,
        not args.no_workspace,
    )
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["write_authorized"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
