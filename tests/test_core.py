"""Testes unitários do content-ops — state, daylog, memory, plan."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Aponta CONTENT_OPS_HOME para um tmp isolado ANTES de importar módulos
_TMP = tempfile.mkdtemp(prefix="content-ops-test-")
os.environ["CONTENT_OPS_HOME"] = _TMP
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content_ops import daylog, memory, plan, state  # noqa: E402


class TestState(unittest.TestCase):
    def test_config_defaults(self):
        cfg = state.get_config()
        self.assertEqual(cfg["blogs"], [])
        self.assertIsNone(cfg["default_blog"])

    def test_state_roundtrip(self):
        st = {"published": [], "covered_projects": {}, "drafts": []}
        st["published"].append({"slug": "x", "title": "X"})
        state.save_state(st)
        st2 = state.get_state()
        self.assertEqual(len(st2["published"]), 1)


class TestDaylog(unittest.TestCase):
    def test_add_and_show(self):
        day = daylog.add_note("trabalhei no Arachne")
        notes = daylog.show(day)
        self.assertEqual(len(notes), 1)
        self.assertIn("Arachne", notes[0]["text"])

    def test_recent(self):
        daylog.add_note("nota de teste")
        rec = daylog.recent(3)
        self.assertGreaterEqual(len(rec), 1)


class TestMemory(unittest.TestCase):
    def test_mark_and_covered(self):
        memory.mark_published("slug-teste", "Título", "capivara")
        self.assertTrue(memory.is_covered("slug-teste"))
        self.assertTrue(memory.is_covered("slug-teste", "capivara"))
        self.assertIn("capivara", memory.covered_projects())

    def test_summary(self):
        s = memory.summary()
        self.assertIn("published_count", s)


class TestPlan(unittest.TestCase):
    def test_suggest_returns_topics(self):
        sugs = plan.suggest(2)
        self.assertLessEqual(len(sugs), 2)
        for s in sugs:
            self.assertIn("project", s)
            self.assertIn("pitch", s)

    def test_weekly_grid_len(self):
        grid = plan.weekly_grid()
        self.assertEqual(len(grid), 7)


if __name__ == "__main__":
    unittest.main()
