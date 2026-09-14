from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from onboarding.bootstrap_project import bootstrap
from onboarding.validate_project import ContractError, validate
from runtime.analyze_repository import analyze
from runtime.intake_gate import intake
from runtime.routing import route


class CoreTests(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "MAU Test"], check=True)
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

    def test_manifest_declared_entrypoint(self):
        repo = self.make_repo()
        bootstrap(repo)
        custom = repo / "checks" / "verify.sh"
        custom.parent.mkdir(parents=True, exist_ok=True)
        custom.write_text("#!/usr/bin/env bash\nexit 4\n", encoding="utf-8")
        manifest_path = repo / ".ai" / "project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["verification"]["command"] = "checks/verify.sh"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        contract = validate(repo, run_verification=True)
        self.assertEqual(contract["verification"], "NOT_APPLICABLE")

    def test_external_orchestrator_requires_evidence(self):
        repo = self.make_repo()
        payload = intake(
            repo,
            request="Change one thing",
            mode="external-orchestrator",
            issue_number=7,
            workspace="/tmp/mau-test-workspace",
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


if __name__ == "__main__":
    unittest.main()
