#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from onboarding.validate_project import ContractError, VERIFICATION_PROFILES, validate
from runtime.analyze_repository import analyze
from runtime.spec_kit_gate import PROFILES as SPEC_KIT_PROFILES
from runtime.spec_kit_gate import verify as verify_spec_kit


WORKFLOW_VERIFICATION = {
    "trivial": "minimal",
    "standard": "focused",
    "full": "full",
    "critical": "critical",
}


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=30)


def _github_repo(origin: str | None) -> str | None:
    if not origin:
        return None
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$", origin)
    return f"{match.group(1)}/{match.group(2)}" if match else None


def finish(
    repository: str | Path,
    issue_number: int | None = None,
    base: str = "main",
    create_pr: bool = True,
    workflow_profile: str | None = None,
    verification_profile: str | None = None,
) -> dict:
    root = Path(analyze(repository)["repository"]["root"])

    spec_kit = None
    if workflow_profile:
        spec_kit = verify_spec_kit(root, workflow_profile)
        if spec_kit["status"] not in {"PASS", "NOT_APPLICABLE"}:
            return {
                "schema_version": 1,
                "kind": "mau.completion",
                "status": "BLOCKED",
                "reason": "Spec Kit workflow artifacts are incomplete",
                "spec_kit": spec_kit,
            }

    selected_verification = verification_profile or WORKFLOW_VERIFICATION.get(workflow_profile or "", None)
    try:
        contract = validate(root, run_verification=True, verification_profile=selected_verification)
    except ContractError as exc:
        return {"schema_version": 1, "kind": "mau.completion", "status": "BLOCKED", "reason": str(exc)}

    verification = contract["verification"]
    if verification not in {"PASS", "NOT_APPLICABLE"}:
        return {
            "schema_version": 1,
            "kind": "mau.completion",
            "status": "BLOCKED",
            "verification": verification,
            "verification_profile": selected_verification,
            "spec_kit": spec_kit,
            "reason": "project verification does not permit completion",
        }

    diffcheck = _run(["git", "diff", "--check"], root)
    if diffcheck.returncode != 0:
        return {
            "schema_version": 1,
            "kind": "mau.completion",
            "status": "BLOCKED",
            "verification": verification,
            "verification_profile": selected_verification,
            "spec_kit": spec_kit,
            "reason": diffcheck.stdout.strip() or diffcheck.stderr.strip() or "git diff --check failed",
        }

    branch = _run(["git", "branch", "--show-current"], root).stdout.strip()
    if not branch or branch == base:
        return {
            "schema_version": 1,
            "kind": "mau.completion",
            "status": "BLOCKED",
            "verification": verification,
            "verification_profile": selected_verification,
            "spec_kit": spec_kit,
            "reason": "work must finish on an isolated non-base branch",
        }

    status = _run(["git", "status", "--porcelain"], root).stdout.strip()
    if status:
        return {
            "schema_version": 1,
            "kind": "mau.completion",
            "status": "BLOCKED",
            "verification": verification,
            "verification_profile": selected_verification,
            "spec_kit": spec_kit,
            "reason": "working tree has uncommitted changes",
        }

    analysis = analyze(root)
    repo = _github_repo(analysis["repository"]["git"]["origin"])
    delivery: dict = {"status": "NOT_RUN"}

    if create_pr:
        if not repo or not shutil.which("gh"):
            delivery = {"status": "UNAVAILABLE", "reason": "GitHub delivery tooling unavailable"}
        else:
            push = _run(["git", "push", "-u", "origin", "HEAD"], root)
            if push.returncode != 0:
                delivery = {"status": "BLOCKED", "reason": push.stderr.strip() or "push failed"}
            else:
                existing = _run(
                    ["gh", "pr", "list", "--repo", repo, "--head", branch, "--state", "open", "--json", "number,url", "--limit", "1"],
                    root,
                )
                matches = json.loads(existing.stdout or "[]") if existing.returncode == 0 else []
                if matches:
                    delivery = {"status": "READY", "source": "existing", **matches[0]}
                else:
                    title = _run(["git", "log", "-1", "--pretty=%s"], root).stdout.strip() or branch
                    body = (
                        "MAU ADS verified delivery.\n\n"
                        f"Verification: {verification}\n"
                        f"Verification profile: {selected_verification or 'default'}\n"
                        f"Workflow profile: {workflow_profile or 'legacy/default'}\n"
                    )
                    if issue_number:
                        body += f"\nCloses #{issue_number}\n"
                    created = _run(
                        ["gh", "pr", "create", "--repo", repo, "--base", base, "--head", branch, "--title", title, "--body", body],
                        root,
                    )
                    if created.returncode == 0:
                        url = created.stdout.strip().splitlines()[-1]
                        number_match = re.search(r"/pull/(\d+)$", url)
                        delivery = {
                            "status": "READY",
                            "source": "created",
                            "url": url,
                            "number": int(number_match.group(1)) if number_match else None,
                        }
                    else:
                        delivery = {"status": "BLOCKED", "reason": created.stderr.strip() or "PR creation failed"}

    overall = "READY_FOR_REVIEW" if (not create_pr or delivery.get("status") == "READY") else "BLOCKED"
    return {
        "schema_version": 1,
        "kind": "mau.completion",
        "status": overall,
        "verification": verification,
        "verification_profile": selected_verification,
        "workflow_profile": workflow_profile,
        "spec_kit": spec_kit,
        "branch": branch,
        "delivery": delivery,
        "production_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Automatic MAU ADS machine-facing completion gate")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--base", default="main")
    parser.add_argument("--no-pr", action="store_true")
    parser.add_argument("--workflow-profile", choices=sorted(SPEC_KIT_PROFILES))
    parser.add_argument("--verification-profile", choices=sorted(VERIFICATION_PROFILES))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = finish(
        args.repository,
        args.issue,
        args.base,
        not args.no_pr,
        args.workflow_profile,
        args.verification_profile,
    )
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["status"] == "READY_FOR_REVIEW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
