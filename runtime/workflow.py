#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from onboarding.validate_project import ContractError, load_manifest, validate
from runtime.completion_gate import finish
from runtime.intake_gate import intake
from runtime.preflight import preflight
from runtime.worker import run_worker


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=60)


def _verification(repository: Path) -> dict:
    try:
        return validate(repository, run_verification=True)
    except ContractError as exc:
        return {"contract": "FAIL", "verification": "NOT_RUN", "error": str(exc)}


def _diff_evidence(repository: Path) -> dict:
    check = _run(["git", "diff", "--check"], repository)
    status = _run(["git", "status", "--porcelain"], repository)
    return {
        "diff_check": "PASS" if check.returncode == 0 else "FAIL",
        "diff_check_output": (check.stdout + check.stderr)[-12000:],
        "has_changes": bool(status.stdout.strip()),
        "status": status.stdout[-12000:],
    }


def _commit(repository: Path, issue_number: int | None, request: str) -> dict:
    add = _run(["git", "add", "-A"], repository)
    if add.returncode != 0:
        return {"status": "FAIL", "reason": add.stderr.strip() or "git add failed"}
    title = request.strip().splitlines()[0][:72] or "MAU ADS change"
    prefix = f"Issue #{issue_number}: " if issue_number else ""
    commit = _run(["git", "commit", "-m", prefix + title], repository)
    if commit.returncode != 0:
        return {"status": "FAIL", "reason": commit.stderr.strip() or commit.stdout.strip() or "git commit failed"}
    sha = _run(["git", "rev-parse", "HEAD"], repository).stdout.strip()
    return {"status": "PASS", "sha": sha}


def _initial_prompt(context: dict) -> str:
    routing = context.get("routing") or {}
    onboarding = context.get("onboarding")
    issue = context.get("work_item") or {}
    onboarding_note = (
        "This workspace was just bootstrapped. Refine PROJECT.md/REPO_MAP.md/.ai/project.json from repository evidence and replace the generated UNAVAILABLE verifier with real project checks before implementing the requested outcome."
        if onboarding else
        "Use the existing project contract and repository evidence."
    )
    return f"""You are the implementation worker inside a MAU ADS isolated workspace.

Canonical work item: GitHub Issue #{issue.get('number')}
Requested outcome:
{context.get('request', '').strip()}

Routing: {json.dumps(routing, sort_keys=True)}

{onboarding_note}

Required behavior:
- Read AGENTS.md, .ai/project.json, PROJECT.md and relevant code before editing.
- Implement the requested outcome completely; do not merely describe it.
- Preserve existing project conventions and minimize unrelated changes.
- Add or strengthen executable verification for the changed behavior where practical.
- For a mauro-php project, preserve the single ignored .env local/production boundary and never copy secrets into tracked files.
- Do not deploy to production.
- Do not create a second GitHub Issue or another worktree.
- Leave all implementation changes uncommitted; MAU ADS owns verification and commit/delivery.
- If a check cannot run, make that explicit rather than claiming success.
"""


def _repair_prompt(context: dict, evidence: dict, attempt: int) -> str:
    return f"""Continue the same MAU ADS task in the same workspace. Attempt {attempt} failed independent gates.

Requested outcome:
{context.get('request', '').strip()}

Failure evidence:
{json.dumps(evidence, indent=2, sort_keys=True)[-24000:]}

Inspect the actual repository state, fix the implementation or verifier as appropriate, and leave changes uncommitted. Do not weaken a correct verification gate merely to obtain PASS.
"""


def run_workflow(
    repository: str | Path,
    request: str,
    issue_number: int | None = None,
    worker_command: str | None = None,
    max_attempts: int | None = None,
    base: str = "main",
    create_pr: bool = True,
    profile: str = "auto",
) -> dict:
    context = intake(
        repository,
        request=request,
        mode="standalone",
        bootstrap_missing=True,
        issue_number=issue_number,
        prepare_workspace=True,
        profile=profile,
    )
    if not context.get("write_authorized"):
        return {"schema_version": 1, "kind": "mau.workflow", "status": "BLOCKED", "stage": "intake", "context": context}

    workspace = Path(context["workspace"]["path"]).expanduser().resolve()
    initial_preflight = preflight(workspace, phase="intake", base=base)
    if initial_preflight["status"] != "PASS":
        return {
            "schema_version": 1,
            "kind": "mau.workflow",
            "status": "BLOCKED",
            "stage": "preflight",
            "context": context,
            "preflight": initial_preflight,
        }

    manifest = load_manifest(workspace)
    configured_attempts = ((manifest.get("workflow") or {}).get("max_fix_attempts") or 3)
    attempts_limit = max_attempts if max_attempts is not None else configured_attempts
    attempts_limit = max(1, min(int(attempts_limit), 10))

    attempts: list[dict] = []
    prompt = _initial_prompt(context)
    success = False
    final_evidence: dict = {}

    for attempt_number in range(1, attempts_limit + 1):
        worker = run_worker(workspace, prompt, command=worker_command)
        verification = _verification(workspace)
        completion_preflight = preflight(workspace, phase="completion", base=base)
        diff = _diff_evidence(workspace)

        pass_state = (
            worker.get("status") == "PASS"
            and verification.get("contract") == "PASS"
            and verification.get("verification") in {"PASS", "NOT_APPLICABLE"}
            and completion_preflight.get("status") == "PASS"
            and diff["diff_check"] == "PASS"
            and diff["has_changes"]
        )
        evidence = {
            "attempt": attempt_number,
            "worker": worker,
            "verification": verification,
            "completion_preflight": completion_preflight,
            "diff": diff,
            "result": "PASS" if pass_state else "FAIL",
        }
        attempts.append(evidence)
        final_evidence = evidence
        if pass_state:
            success = True
            break
        if attempt_number < attempts_limit:
            prompt = _repair_prompt(context, evidence, attempt_number + 1)

    if not success:
        return {
            "schema_version": 1,
            "kind": "mau.workflow",
            "status": "BLOCKED",
            "stage": "verification",
            "context": context,
            "attempts": attempts,
            "final_evidence": final_evidence,
        }

    commit = _commit(workspace, context.get("work_item", {}).get("number"), request)
    if commit["status"] != "PASS":
        return {
            "schema_version": 1,
            "kind": "mau.workflow",
            "status": "BLOCKED",
            "stage": "commit",
            "context": context,
            "attempts": attempts,
            "commit": commit,
        }

    delivery = finish(
        workspace,
        issue_number=context.get("work_item", {}).get("number"),
        base=base,
        create_pr=create_pr,
    )
    overall = "READY" if delivery.get("status") == "READY_FOR_REVIEW" else "BLOCKED"
    return {
        "schema_version": 1,
        "kind": "mau.workflow",
        "status": overall,
        "stage": "complete" if overall == "READY" else "delivery",
        "context": context,
        "attempts": attempts,
        "commit": commit,
        "delivery": delivery,
        "production_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the complete MAU ADS request-to-ready workflow")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--request", required=True)
    parser.add_argument("--issue", type=int)
    parser.add_argument("--worker-command")
    parser.add_argument("--max-attempts", type=int)
    parser.add_argument("--base", default="main")
    parser.add_argument("--profile", choices=("auto", "generic", "mauro-php"), default="auto")
    parser.add_argument("--no-pr", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = run_workflow(
        args.repository,
        args.request,
        issue_number=args.issue,
        worker_command=args.worker_command,
        max_attempts=args.max_attempts,
        base=args.base,
        create_pr=not args.no_pr,
        profile=args.profile,
    )
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["status"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
