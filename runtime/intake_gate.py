#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from onboarding.bootstrap_project import bootstrap
from onboarding.onboarding_gate import evaluate as evaluate_onboarding
from onboarding.validate_project import ContractError, validate
from runtime.analyze_repository import analyze
from runtime.routing import route
from runtime.spec_kit import status as spec_kit_status
from runtime.spec_kit_gate import clarification_state


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


def _onboarding_execution_status(onboarding: dict) -> str:
    mapping = {
        "NEEDS_ASSESSMENT": "NEEDS_ONBOARDING_ASSESSMENT",
        "NEEDS_CLARIFICATION": "NEEDS_ONBOARDING_CLARIFICATION",
        "NEEDS_VERIFICATION_SETUP": "NEEDS_ONBOARDING_VERIFICATION",
        "BLOCKED": "NEEDS_RECONCILE",
    }
    return mapping.get(onboarding.get("status"), "NEEDS_RECONCILE")


def _execution_contract(routing: dict, work: dict, onboarding: dict) -> dict:
    workflow = routing["workflow"]
    verification = routing["verification"]

    if onboarding.get("status") != "READY":
        actions = list(onboarding.get("actions", []))
        if not any(action.get("type") == "rerun_intake" for action in actions if isinstance(action, dict)):
            actions.append({"type": "rerun_intake", "after": "onboarding_reconciliation"})
        return {
            "status": _onboarding_execution_status(onboarding),
            "blocked_by": "onboarding",
            "engine": workflow["engine"],
            "workflow_profile": workflow["profile"],
            "required_sequence": workflow["sequence"],
            "pre_implementation_sequence": ["mau.onboarding-gate"],
            "verification_profile": verification["profile"],
            "verification_minimum": verification["minimum"],
            "model_policy": routing["model_policy"],
            "onboarding_required": True,
            "onboarding": onboarding,
            "spec_kit_required": workflow["engine"] == "spec-kit",
            "spec_kit": None,
            "clarification_required": workflow["engine"] == "spec-kit",
            "clarification": None,
            "actions": actions,
        }

    workspace = work.get("path") if work.get("status") == "READY" else None
    requires_spec_kit = workflow["engine"] == "spec-kit"
    kit = spec_kit_status(workspace) if requires_spec_kit and workspace else None
    clarification = None

    if requires_spec_kit and workspace and kit and kit.get("status") == "READY":
        clarification = clarification_state(workspace)

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

    if requires_spec_kit and kit and kit.get("status") == "READY":
        clarity_status = clarification.get("status") if clarification else "NOT_ASSESSED"
        if clarity_status == "NOT_ASSESSED":
            actions.append(
                {
                    "type": "assess_requirements",
                    "workspace": workspace,
                    "sequence": ["speckit.specify", "speckit.clarify", "write_clarification_artifact", "rerun_intake"],
                    "artifact": "<active-feature>/clarification.json",
                    "rule": "repository facts first; ask the user only for unresolved functional, risk or irreversible decisions",
                }
            )
        elif clarity_status == "NEEDS_USER":
            actions.extend(
                [
                    {
                        "type": "ask_user",
                        "questions": clarification.get("open_questions", []),
                        "reason": clarification.get("reason"),
                    },
                    {
                        "type": "record_clarification_answers",
                        "artifact": clarification.get("artifact"),
                        "after": "ask_user",
                    },
                    {"type": "rerun_intake", "after": "record_clarification_answers"},
                ]
            )
        elif clarity_status == "BLOCKED":
            actions.extend(
                [
                    {
                        "type": "repair_clarification_artifact",
                        "artifact": clarification.get("artifact"),
                        "reason": clarification.get("reason"),
                    },
                    {"type": "rerun_intake", "after": "repair_clarification_artifact"},
                ]
            )

    if not requires_spec_kit or (
        kit and kit.get("status") == "READY" and clarification and clarification.get("status") == "PASS"
    ):
        actions.append(
            {
                "type": "complete_work",
                "workspace": workspace,
                "workflow_profile": workflow["profile"],
                "verification_profile": verification["profile"],
            }
        )

    if not requires_spec_kit:
        execution_status = "READY"
    elif not kit or kit.get("status") != "READY":
        execution_status = "NEEDS_RECONCILE"
    elif not clarification or clarification.get("status") == "NOT_ASSESSED":
        execution_status = "NEEDS_CLARIFICATION_ASSESSMENT"
    elif clarification.get("status") == "NEEDS_USER":
        execution_status = "NEEDS_CLARIFICATION"
    elif clarification.get("status") == "PASS":
        execution_status = "READY"
    else:
        execution_status = "NEEDS_RECONCILE"

    return {
        "status": execution_status,
        "engine": workflow["engine"],
        "workflow_profile": workflow["profile"],
        "required_sequence": workflow["sequence"],
        "pre_implementation_sequence": (
            ["mau.onboarding-gate", "speckit.specify", "speckit.clarify", "mau.clarification-gate"]
            if requires_spec_kit
            else ["mau.onboarding-gate", "inspect"]
        ),
        "verification_profile": verification["profile"],
        "verification_minimum": verification["minimum"],
        "model_policy": routing["model_policy"],
        "onboarding_required": True,
        "onboarding": onboarding,
        "spec_kit_required": requires_spec_kit,
        "spec_kit": kit,
        "clarification_required": requires_spec_kit,
        "clarification": clarification,
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
    bootstrap_result = None

    try:
        contract = validate(root, False)
    except ContractError:
        if not bootstrap_missing:
            contract = {"contract": "FAIL", "verification": "NOT_RUN"}
        else:
            bootstrap_result = bootstrap(root)
            contract = validate(root, False)

    analysis = analyze(root)
    onboarding = evaluate_onboarding(root) if contract.get("contract") == "PASS" else {
        "status": "BLOCKED",
        "user_input_required": False,
        "reason": "repository contract is invalid",
        "actions": [{"type": "repair_project_contract"}],
    }
    routing = route(request)
    onboarding_ready = onboarding.get("status") == "READY"

    if mode == "standalone":
        if onboarding_ready:
            issue = {"status": "READY", "source": "provided", "number": issue_number} if issue_number else _resolve_or_create_issue(root, request, analysis["repository"]["git"]["origin"])
            work = _prepare_worktree(root, issue, request) if prepare_workspace else {"status": "NOT_RUN", "reason": "workspace preparation disabled"}
            write_authorized = contract.get("contract") == "PASS" and issue.get("status") == "READY" and work.get("status") == "READY"
        else:
            issue = {"status": "NOT_RUN", "reason": "repository onboarding must become READY before feature work identity is created"}
            work = {"status": "NOT_RUN", "reason": "repository onboarding must become READY before implementation workspace creation"}
            write_authorized = contract.get("contract") == "PASS"
        delegated: list[str] = []
    else:
        issue = {"status": "READY" if issue_number else "REQUIRED", "source": "orchestrator", "number": issue_number}
        work = {"status": "READY" if workspace else "REQUIRED", "source": "orchestrator", "path": workspace}
        if onboarding_ready:
            write_authorized = contract.get("contract") == "PASS" and bool(issue_number) and bool(workspace)
        else:
            write_authorized = contract.get("contract") == "PASS"
        delegated = ["work_item", "workspace_isolation", "worker_dispatch", "github_delivery"]

    execution = _execution_contract(routing, work, onboarding)
    implementation_authorized = write_authorized and onboarding_ready and execution["status"] == "READY"
    reconciliation_scope: list[str] = []
    if write_authorized and not implementation_authorized:
        if not onboarding_ready:
            reconciliation_scope = ["project-contract", "onboarding-state", "project-docs", "project-verifier"]
        else:
            reconciliation_scope = ["spec-kit-setup", "spec-kit-artifacts", "clarification-artifact"]

    return {
        "schema_version": 4,
        "kind": "mau.work_context",
        "mode": mode,
        "request": request,
        "repository": {
            "root": str(root),
            "fingerprint": analysis["structure"]["fingerprint"],
            "contract": contract["contract"],
        },
        "bootstrap": bootstrap_result,
        "onboarding": onboarding,
        "work_item": issue,
        "workspace": work,
        "routing": routing,
        "execution": execution,
        "delegated_to_orchestrator": delegated,
        "write_authorized": write_authorized,
        "implementation_authorized": implementation_authorized,
        "user_input_required": bool(onboarding.get("user_input_required")) or execution["status"] == "NEEDS_CLARIFICATION",
        "gate_reconciliation_authorized": write_authorized and not implementation_authorized,
        "gate_reconciliation_scope": reconciliation_scope,
        "completion_requires": {
            "onboarding_gate": True,
            "workflow_artifacts": execution["spec_kit_required"],
            "clarification_gate": execution["clarification_required"],
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
