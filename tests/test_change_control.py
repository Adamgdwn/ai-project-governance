import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import change_control


class ChangeControlTests(unittest.TestCase):
    def test_manifest_adds_use_case_standard_without_overriding_risk(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "sample-agent"
            project.mkdir()
            (project / "README.md").write_text("# Sample\n", encoding="utf-8")
            (project / "AGENTS.md").write_text("# Agent Rules\n", encoding="utf-8")

            manifest = change_control.build_manifest(project)
            paths = {action["relative_path"] for action in manifest["actions"]}

            self.assertIn("docs/standards/engineering-governance-by-use-case.md", paths)
            self.assertIn("docs/policy/durable-development-engineering-policy.md", paths)
            self.assertIn("project-control.yaml", paths)
            self.assertTrue(any(action.get("block_id") == change_control.USE_CASE_BLOCK_ID for action in manifest["actions"]))

            manifest_path = project / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            change_control.apply_manifest(manifest_path)

            control = (project / "project-control.yaml").read_text(encoding="utf-8")
            self.assertIn("project_type: agent", control)
            self.assertIn("risk_tier: low", control)
            self.assertIn("governance_level: 1", control)
            self.assertIn("primary: AI agent with tools", control)

            second_manifest = change_control.build_manifest(project)
            self.assertEqual([], second_manifest["actions"])


if __name__ == "__main__":
    unittest.main()
