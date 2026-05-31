import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import env_sync


class EnvSyncTests(unittest.TestCase):
    def test_parse_env_value_and_privileged_classification(self):
        self.assertEqual("hello world", env_sync.parse_env_value('"hello world"'))
        self.assertEqual("value", env_sync.parse_env_value("value # comment"))
        self.assertTrue(env_sync.is_privileged_key("SUPABASE_SERVICE_ROLE_KEY"))
        self.assertFalse(env_sync.is_privileged_key("NEXT_PUBLIC_SUPABASE_URL"))
        self.assertFalse(env_sync.is_privileged_key("STRIPE_PUBLISHABLE_KEY"))

    def test_build_sync_plan_redacts_values_and_counts_privileged_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            (project / ".env.example").write_text(
                "NEXT_PUBLIC_SUPABASE_URL=\nSUPABASE_SERVICE_ROLE_KEY=\nMISSING_KEY=\n",
                encoding="utf-8",
            )
            master = root / ".env.master"
            master.write_text(
                "NEXT_PUBLIC_SUPABASE_URL=https://example.supabase.co\n"
                "SUPABASE_SERVICE_ROLE_KEY=service-role-secret\n",
                encoding="utf-8",
            )

            plan = env_sync.build_sync_plan(project, master, ".env.local", False, [])
            entries = {entry["key"]: entry for entry in plan["entries"]}

            self.assertEqual("ready", entries["NEXT_PUBLIC_SUPABASE_URL"]["status"])
            self.assertFalse(entries["NEXT_PUBLIC_SUPABASE_URL"]["privileged"])
            self.assertEqual("ready", entries["SUPABASE_SERVICE_ROLE_KEY"]["status"])
            self.assertTrue(entries["SUPABASE_SERVICE_ROLE_KEY"]["privileged"])
            self.assertEqual("missing_from_master", entries["MISSING_KEY"]["status"])
            self.assertEqual(1, plan["summary"]["privileged_ready"])
            self.assertNotIn("service-role-secret", str(plan))


if __name__ == "__main__":
    unittest.main()
