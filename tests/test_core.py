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
from runtime.spec_kit_gate import verify as verify_spec_kit


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

    def make_spec_feature(self, repo: Path, tasks: str = "- [x] T001 Done\n") -> Path:
        feature = repo / "specs" / "001-example"
        feature.mkdir(parents=True)
        (feature / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (feature / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (feature / "tasks.md").write_text(tasks, encoding="utf-8")
        specify = repo / ".specify"
        specify.mkdir()
        (specify / "feature.json").write_text(
            json.dumps({"feature_directory": "specs/001-example"}),
            encoding="utf-8",
        )
        return feature

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

    def test_verification_profile_is_passed_to_project_check(self):
        repo = self.make_repo()
        bootstrap(repo)
        custom = repo / "checks" / "verify.sh"
        custom.parent.mkdir(parents=True, exist_ok=True)
        custom.write_text(
            "#!/usr/bin/env bash\n"
            "test \"${MAU_VERIFICATION_PROFILE:-}\" = \"minimal\"\n",
            encoding="utf-8",
        )
        manifest_path = repo / ".ai" / "project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["verification"]["command"] = "checks/verify.sh"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        contract = validate(repo, run_verification=True, verification_profile="minimal")
        self.assertEqual(contract["verification"], "PASS")
        self.assertEqual(contract["verification_profile"], "minimal")

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
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["execution"]["workflow_profile"], "standard")

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
        self.assertEqual(routed["complexity"]["level"], "COMPLEX")
        self.assertEqual(routed["workflow"]["profile"], "full")
        self.assertEqual(routed["verification"]["profile"], "full")
        self.assertIn("persistent-data-safety", routed["capabilities"])

    def test_trivial_label_change_uses_minimum_workflow(self):
        routed = route("Cambia l'etichetta del pulsante da Salva a Conferma")
        self.assertEqual(routed["risk"]["level"], "NORMAL")
        self.assertEqual(routed["complexity"]["level"], "TRIVIAL")
        self.assertEqual(routed["workflow"]["engine"], "direct")
        self.assertEqual(routed["workflow"]["profile"], "trivial")
        self.assertEqual(routed["verification"]["profile"], "minimal")
        self.assertEqual(routed["model_policy"]["implementation"], "economy")

    def test_new_section_uses_full_spec_kit_workflow(self):
        routed = route("Aggiungi una nuova sezione del gestionale per lo storico controlli")
        self.assertEqual(routed["complexity"]["level"], "COMPLEX")
        self.assertEqual(routed["workflow"]["engine"], "spec-kit")
        self.assertEqual(routed["workflow"]["profile"], "full")
        self.assertIn("speckit.plan", routed["workflow"]["sequence"])
        self.assertEqual(routed["verification"]["profile"], "full")

    def test_spec_kit_gate_blocks_incomplete_tasks(self):
        repo = self.make_repo()
        self.make_spec_feature(repo, tasks="- [ ] T001 Implement\n")
        result = verify_spec_kit(repo, "standard")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("T001", result["open_tasks"][0])

    def test_spec_kit_gate_passes_complete_feature(self):
        repo = self.make_repo()
        self.make_spec_feature(repo)
        result = verify_spec_kit(repo, "full")
        self.assertEqual(result["status"], "PASS")

    def test_critical_spec_kit_gate_requires_complete_checklists(self):
        repo = self.make_repo()
        feature = self.make_spec_feature(repo)
        checklists = feature / "checklists"
        checklists.mkdir()
        (checklists / "safety.md").write_text("- [ ] Verify rollback\n", encoding="utf-8")
        result = verify_spec_kit(repo, "critical")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("Verify rollback", result["open_checklist_items"][0])


if __name__ == "__main__":
    unittest.main()
