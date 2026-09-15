from __future__ import annotations

import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from onboarding.bootstrap_project import bootstrap
from onboarding.validate_project import ContractError, validate
from runtime.analyze_repository import analyze
from runtime.intake_gate import intake
from runtime.routing import route
from runtime.workflow import run_workflow


class CoreTests(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "MAU Test"], check=True)
        subprocess.run(["git", "-C", str(root), "branch", "-M", "main"], check=True)
        (root / "README.md").write_text("# Example\n\nA small example repository.\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
        return root

    def test_analyzer_is_read_only(self):
        repo = self.make_repo()
        before = subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain"], text=True)
        data = analyze(repo)
        after = subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain"], text=True)
        self.assertEqual(before, after)
        self.assertEqual(data["kind"], "mau.repository_analysis")
        self.assertIn("AGENTS.md", data["contract"]["missing"])

    def test_bootstrap_never_fakes_pass(self):
        repo = self.make_repo()
        result = bootstrap(repo)
        self.assertIn("AGENTS.md", result["created"])
        contract = validate(repo, run_verification=True)
        self.assertEqual(contract["contract"], "PASS")
        self.assertEqual(contract["verification"], "UNAVAILABLE")
        self.assertIn("not configured", contract["verification_stderr"])

    def test_mauro_php_bootstrap_describes_environment_without_secrets(self):
        repo = self.make_repo()
        (repo / "configure.php").write_text("<?php\n", encoding="utf-8")
        (repo / "index.php").write_text("<?php\n", encoding="utf-8")
        result = bootstrap(repo, profile="mauro-php")
        manifest = json.loads((repo / ".ai" / "project.json").read_text(encoding="utf-8"))
        self.assertEqual(result["profile"], "mauro-php")
        self.assertEqual(manifest["environments"]["local"]["runtime_files"], [".env"])
        self.assertEqual(manifest["environments"]["production"]["deployment_authorization"], "explicit")
        self.assertIn(".env", (repo / ".gitignore").read_text(encoding="utf-8").splitlines())
        self.assertNotIn("password", json.dumps(manifest).lower())

    def test_manifest_declared_entrypoint(self):
        repo = self.make_repo()
        bootstrap(repo)
        custom = repo / "checks" / "verify.sh"
        custom.parent.mkdir(parents=True, exist_ok=True)
        custom.write_text("#!/usr/bin/env bash\necho skip\nexit 4\n", encoding="utf-8")
        manifest_path = repo / ".ai" / "project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["verification"]["command"] = "checks/verify.sh"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        contract = validate(repo, run_verification=True)
        self.assertEqual(contract["verification"], "NOT_APPLICABLE")
        self.assertIn("skip", contract["verification_stdout"])

    def test_external_orchestrator_requires_evidence(self):
        repo = self.make_repo()
        payload = intake(
            repo,
            request="Change one thing",
            mode="external-orchestrator",
            issue_number=7,
            workspace=str(repo),
            prepare_workspace=False,
        )
        self.assertTrue(payload["write_authorized"])
        self.assertIn("work_item", payload["delegated_to_orchestrator"])

    def test_bad_schema_is_rejected(self):
        repo = self.make_repo()
        bootstrap(repo)
        manifest_path = repo / ".ai" / "project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["schema_version"] = 99
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(ContractError):
            validate(repo)

    def test_routing_marks_sensitive_work(self):
        routed = route("Update database schema and migration")
        self.assertEqual(routed["risk"]["level"], "ELEVATED")
        self.assertIn("persistent-data-safety", routed["capabilities"])

    def make_worker(self, body: str) -> Path:
        path = Path(tempfile.mkdtemp()) / "worker.py"
        path.write_text("import sys\nfrom pathlib import Path\nroot = Path.cwd()\n_ = sys.stdin.read()\n" + textwrap.dedent(body), encoding="utf-8")
        return path

    def test_workflow_reaches_ready_with_independent_verification(self):
        repo = self.make_repo()
        worker = self.make_worker(
            """
            (root / "feature.txt").write_text("implemented\\n", encoding="utf-8")
            verify = root / "dev" / "verify-local.sh"
            verify.write_text("#!/usr/bin/env bash\\nset -euo pipefail\\ntest -f feature.txt\\nexit 0\\n", encoding="utf-8")
            verify.chmod(0o755)
            """
        )
        result = run_workflow(
            repo,
            "Implement deterministic example feature",
            issue_number=101,
            worker_command=f"python3 {worker}",
            max_attempts=2,
            create_pr=False,
        )
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["delivery"]["verification"], "PASS")
        self.assertEqual(len(result["attempts"]), 1)
        self.assertEqual(result["attempts"][0]["result"], "PASS")

    def test_workflow_repairs_after_failed_verification(self):
        repo = self.make_repo()
        counter = Path(tempfile.mkdtemp()) / "count.txt"
        worker = self.make_worker(
            f"""
            counter = Path({str(counter)!r})
            count = int(counter.read_text() if counter.exists() else "0") + 1
            counter.write_text(str(count), encoding="utf-8")
            (root / "feature.txt").write_text("attempt=" + str(count) + "\\n", encoding="utf-8")
            if count >= 2:
                verify = root / "dev" / "verify-local.sh"
                verify.write_text("#!/usr/bin/env bash\\nset -euo pipefail\\ngrep -q 'attempt=2' feature.txt\\nexit 0\\n", encoding="utf-8")
                verify.chmod(0o755)
            """
        )
        result = run_workflow(
            repo,
            "Implement with repair loop",
            issue_number=102,
            worker_command=f"python3 {worker}",
            max_attempts=3,
            create_pr=False,
        )
        self.assertEqual(result["status"], "READY")
        self.assertEqual(len(result["attempts"]), 2)
        self.assertEqual(result["attempts"][0]["verification"]["verification"], "UNAVAILABLE")
        self.assertEqual(result["attempts"][1]["result"], "PASS")

    def test_workflow_never_promotes_unavailable_verification_to_ready(self):
        repo = self.make_repo()
        worker = self.make_worker(
            """
            (root / "feature.txt").write_text("changed\\n", encoding="utf-8")
            """
        )
        result = run_workflow(
            repo,
            "Make a change without configuring verification",
            issue_number=103,
            worker_command=f"python3 {worker}",
            max_attempts=2,
            create_pr=False,
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["stage"], "verification")
        self.assertEqual(len(result["attempts"]), 2)
        self.assertTrue(all(item["result"] == "FAIL" for item in result["attempts"]))


if __name__ == "__main__":
    unittest.main()
