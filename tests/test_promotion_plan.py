import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import promotion_plan


class PromotionPlanTests(unittest.TestCase):
    def test_local_checks_detect_python_shell_and_unittest(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            (project / "automation").mkdir(parents=True)
            (project / "scripts").mkdir()
            (project / "tests").mkdir()
            (project / "automation" / "tool.py").write_text("print('ok')\n", encoding="utf-8")
            (project / "scripts" / "governance-preflight.sh").write_text("#!/usr/bin/env bash\ntrue\n", encoding="utf-8")
            (project / "tests" / "test_sample.py").write_text("import unittest\n", encoding="utf-8")

            checks = promotion_plan.build_local_checks(project)
            names = {check["name"] for check in checks["pre"]}

            self.assertIn("governance_preflight", names)
            self.assertIn("python_compile", names)
            self.assertIn("shell_syntax", names)
            self.assertIn("python_unittest", names)
            self.assertNotIn("manual_smoke_review", names)
            self.assertTrue(all("argv" in check for check in checks["pre"]))


if __name__ == "__main__":
    unittest.main()
