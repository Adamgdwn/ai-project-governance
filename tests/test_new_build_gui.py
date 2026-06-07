import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import new_build_gui


class NewBuildGuiTests(unittest.TestCase):
    def test_window_fonts_are_scaled_for_readability(self):
        self.assertEqual(new_build_gui.FONT_SCALE, 2)
        self.assertEqual(new_build_gui.FONT, ("Sans", 20))
        self.assertEqual(new_build_gui.SMALL, ("Sans", 18))
        self.assertEqual(new_build_gui.TITLE, ("Sans", 36, "bold"))
        self.assertEqual(new_build_gui.MONO, ("Monospace", 18))

    def test_activity_log_is_compact_by_default(self):
        self.assertTrue(new_build_gui.ACTIVITY_LOG_COLLAPSED_BY_DEFAULT)
        self.assertEqual(new_build_gui.ACTIVITY_LOG_EXPANDED_HEIGHT, 6)

    def test_update_affordance_allows_only_fast_forward(self):
        summary, allowed = new_build_gui.build_update_affordance_summary("behind", "would_update")

        self.assertTrue(allowed)
        self.assertIn("Safe fast-forward update is available.", summary)

    def test_update_affordance_blocks_refused_state(self):
        summary, allowed = new_build_gui.build_update_affordance_summary("behind", "refused")

        self.assertFalse(allowed)
        self.assertIn("blocked", summary)

    def test_update_affordance_blocks_up_to_date_state(self):
        summary, allowed = new_build_gui.build_update_affordance_summary("current", "up_to_date")

        self.assertFalse(allowed)
        self.assertIn("already up to date", summary)


if __name__ == "__main__":
    unittest.main()
