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
            self.assertIn("docs/standards/README.md", paths)
            self.assertIn("docs/standards/ship-ready-engineering-standard.md", paths)
            self.assertIn("docs/standards/context-hygiene-standard.md", paths)
            self.assertIn("docs/domain-language.md", paths)
            self.assertIn("project-control.yaml", paths)
            self.assertTrue(any(action.get("block_id") == change_control.USE_CASE_BLOCK_ID for action in manifest["actions"]))
            self.assertTrue(any(action.get("block_id") == change_control.SHIP_READY_BLOCK_ID for action in manifest["actions"]))
            self.assertTrue(any(action.get("block_id") == change_control.CONTEXT_HYGIENE_BLOCK_ID for action in manifest["actions"]))
            self.assertTrue(any(action.get("block_id") == change_control.FUNDAMENTALS_BLOCK_ID for action in manifest["actions"]))
            self.assertTrue(any(action.get("block_id") == change_control.GRAPHIFY_BLOCK_ID for action in manifest["actions"]))

            manifest_path = project / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            change_control.apply_manifest(manifest_path)

            control = (project / "project-control.yaml").read_text(encoding="utf-8")
            self.assertIn("project_type: agent", control)
            self.assertIn("risk_tier: low", control)
            self.assertIn("governance_level: 1", control)
            self.assertIn("primary: AI agent with tools", control)
            agent_rules = (project / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("Fundamentals-First AI Coding", agent_rules)
            self.assertIn("AI speed does not make bad code cheap", agent_rules)
            self.assertIn("smallest safe improvement", agent_rules)
            self.assertIn("Context Hygiene Managed Instructions", agent_rules)
            self.assertIn("context-hygiene-standard.md", agent_rules)
            self.assertIn("targeted diffs", agent_rules)
            self.assertIn("Graphify Policy", agent_rules)
            self.assertIn("GRAPHIFY_AGENT_GOVERNANCE.md", agent_rules)
            self.assertIn("graphify-out/graph.json", agent_rules)
            self.assertIn("graphify update . --no-cluster --force", agent_rules)
            self.assertIn("do not index, print, summarize, or commit secrets", agent_rules)
            domain_language = (project / "docs" / "domain-language.md").read_text(encoding="utf-8")
            self.assertIn("# Domain Language", domain_language)
            self.assertIn("Avoid Saying", domain_language)
            standards_index = (project / "docs" / "standards" / "README.md").read_text(encoding="utf-8")
            self.assertIn("# Engineering Standards Index", standards_index)
            self.assertIn("Ship-Ready Engineering Standard", standards_index)
            self.assertIn("Context Hygiene Standard", standards_index)
            ship_ready = (project / "docs" / "standards" / "ship-ready-engineering-standard.md").read_text(encoding="utf-8")
            self.assertIn("# Ship-Ready Engineering Standard", ship_ready)
            self.assertIn("Definition Of Shipped", ship_ready)
            context_hygiene = (project / "docs" / "standards" / "context-hygiene-standard.md").read_text(encoding="utf-8")
            self.assertIn("# Context Hygiene Standard", context_hygiene)
            self.assertIn("Handoff Summary Template", context_hygiene)

            second_manifest = change_control.build_manifest(project)
            self.assertEqual([], second_manifest["actions"])

    def test_document_control_manifest_syncs_standard_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "existing-repo"
            project.mkdir()

            manifest = change_control.build_document_control_manifest(project)
            self.assertEqual("document_control_update", manifest["manifest_kind"])
            self.assertEqual(["docs/standards/document-control-standard.md"], [action["relative_path"] for action in manifest["actions"]])

            manifest_path = project / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            change_control.apply_manifest(manifest_path)

            target = project / "docs" / "standards" / "document-control-standard.md"
            self.assertEqual(change_control.DOCUMENT_CONTROL_STANDARD.read_text(encoding="utf-8"), target.read_text(encoding="utf-8"))
            self.assertEqual([], change_control.build_document_control_manifest(project)["actions"])


if __name__ == "__main__":
    unittest.main()
