from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from onboarding.bootstrap_project import bootstrap
from onboarding.onboarding_gate import evaluate, finalize
from runtime.intake_gate import intake


class OnboardingGateTests(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "MAU Test"], check=True)
        (root / "README.md").write_text("# Example application\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
        return root

    def resolve_assessment(self, repo: Path) -> dict:
        state_path = repo / ".ai" / "onboarding.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["purpose"] = {
            "status": "RESOLVED",
            "summary": "Example application used by MAU tests",
            "evidence": ["repository:README.md"],
        }
        state["canonical_source"] = {
            "status": "RESOLVED",
            "path": ".",
            "evidence": ["repository:git-root"],
        }
        state["questions"] = []
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return state

    def install_real_verifier(self, repo: Path) -> None:
        verifier = repo / "dev" / "verify-local.sh"
        verifier.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "test \"${MAU_VERIFICATION_PROFILE:-}\" = \"focused\"\n"
            "test -f README.md\n",
            encoding="utf-8",
        )
        verifier.chmod(verifier.stat().st_mode | 0o111)

    def test_bootstrap_creates_docs_and_requires_assessment(self):
        repo = self.make_repo()
        result = bootstrap(repo)
        self.assertIn("AGENTS.md", result["created"])
        self.assertIn("PROJECT.md", result["created"])
        self.assertIn("REPO_MAP.md", result["created"])
        self.assertIn(".ai/onboarding.json", result["created"])
        gate = evaluate(repo)
        self.assertEqual(gate["status"], "NEEDS_ASSESSMENT")
        self.assertFalse(gate["user_input_required"])

    def test_open_onboarding_question_requires_user_input(self):
        repo = self.make_repo()
        bootstrap(repo)
        state_path = repo / ".ai" / "onboarding.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["questions"] = [
            {
                "id": "O1",
                "category": "ownership",
                "question": "Quale cartella contiene la sorgente canonica dell'applicazione?",
                "status": "OPEN",
                "answer": None,
                "source": None,
            }
        ]
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        gate = evaluate(repo)
        self.assertEqual(gate["status"], "NEEDS_CLARIFICATION")
        self.assertTrue(gate["user_input_required"])
        self.assertEqual(gate["open_questions"][0]["id"], "O1")

    def test_real_verification_must_pass_before_ready(self):
        repo = self.make_repo()
        bootstrap(repo)
        self.resolve_assessment(repo)
        before = evaluate(repo)
        self.assertEqual(before["status"], "NEEDS_VERIFICATION_SETUP")
        self.install_real_verifier(repo)
        result = finalize(repo)
        self.assertEqual(result["status"], "READY")
        after = evaluate(repo)
        self.assertEqual(after["status"], "READY")
        self.assertEqual(after["verification_baseline"], "PASS")

    def test_verifier_change_invalidates_ready_onboarding(self):
        repo = self.make_repo()
        bootstrap(repo)
        self.resolve_assessment(repo)
        self.install_real_verifier(repo)
        self.assertEqual(finalize(repo)["status"], "READY")
        verifier = repo / "dev" / "verify-local.sh"
        verifier.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        gate = evaluate(repo)
        self.assertEqual(gate["status"], "NEEDS_VERIFICATION_SETUP")
        self.assertIn("changed after onboarding baseline", gate["reason"])

    def test_intake_blocks_feature_work_until_onboarding_ready(self):
        repo = self.make_repo()
        payload = intake(
            repo,
            request="Aggiungi una nuova sezione clienti",
            mode="external-orchestrator",
            issue_number=7,
            workspace="/tmp/mau-test-workspace",
            prepare_workspace=False,
        )
        self.assertTrue(payload["write_authorized"])
        self.assertFalse(payload["implementation_authorized"])
        self.assertTrue(payload["gate_reconciliation_authorized"])
        self.assertEqual(payload["execution"]["status"], "NEEDS_ONBOARDING_ASSESSMENT")
        self.assertEqual(payload["execution"]["blocked_by"], "onboarding")
        self.assertIn("project-verifier", payload["gate_reconciliation_scope"])


if __name__ == "__main__":
    unittest.main()
