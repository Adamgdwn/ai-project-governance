import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import promotion_execute


class PromotionExecuteTests(unittest.TestCase):
    def test_choose_stage_files_requires_explicit_decision(self):
        changed = [" M README.md", "?? docs/new.md"]

        with self.assertRaisesRegex(RuntimeError, "requires an explicit staged file decision"):
            promotion_execute.choose_stage_files(changed, [], False)

        mode, files = promotion_execute.choose_stage_files(changed, ["README.md"], False)
        self.assertEqual("explicit_file_list", mode)
        self.assertEqual(["README.md"], files)

        mode, files = promotion_execute.choose_stage_files(changed, [], True)
        self.assertEqual("approved_full_working_tree", mode)
        self.assertEqual(["README.md", "docs/new.md"], files)

    def test_choose_stage_files_blocks_secret_like_paths(self):
        with self.assertRaisesRegex(RuntimeError, "secret-like paths"):
            promotion_execute.choose_stage_files(["?? .env.local"], [".env.local"], False)


if __name__ == "__main__":
    unittest.main()
