from __future__ import annotations

import unittest

from onboarding.validate_project import ContractError
from runtime.completion_gate import _resolve_verification_profile


class CompletionProfileTests(unittest.TestCase):
    def test_workflow_default_selects_minimum_verification(self):
        self.assertEqual(_resolve_verification_profile("trivial", None), "minimal")
        self.assertEqual(_resolve_verification_profile("standard", None), "focused")
        self.assertEqual(_resolve_verification_profile("full", None), "full")
        self.assertEqual(_resolve_verification_profile("critical", None), "critical")

    def test_completion_rejects_verification_downgrade(self):
        with self.assertRaises(ContractError):
            _resolve_verification_profile("critical", "minimal")
        with self.assertRaises(ContractError):
            _resolve_verification_profile("full", "focused")

    def test_completion_accepts_stronger_verification(self):
        self.assertEqual(_resolve_verification_profile("standard", "full"), "full")
        self.assertEqual(_resolve_verification_profile("full", "critical"), "critical")


if __name__ == "__main__":
    unittest.main()
