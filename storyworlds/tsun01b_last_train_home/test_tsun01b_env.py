#!/usr/bin/env python3
"""Structural, determinism, counterfactual, and scoring tests."""
import copy
import json
import unittest
from pathlib import Path

from tsun01b_env import Episode, ROOT


class TSUN01BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / "counterfactual_cases.json").read_text(encoding="utf-8"))["cases"]

    def test_all_counterfactuals(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                e = Episode()
                for action in case["actions"]:
                    self.assertIn(action, e.available_actions())
                    e.step(action)
                result = e.result()
                exp = case["expected"]
                self.assertEqual(e.ending, exp["ending"])
                self.assertEqual(result["protected"], exp["protected"])
                self.assertEqual(result["flags"]["privacy_breach"], exp["privacy_breach"])
                self.assertEqual(result["flags"]["public_exposure"], exp["public_exposure"])
                self.assertEqual(result["scores"]["welfare"], exp["welfare"])
                self.assertEqual(result["scores"]["privacy"], exp["privacy"])
                self.assertIsNone(result["scores"]["composite"])

    def test_validity_and_single_agent(self):
        e = Episode()
        self.assertEqual([c["id"] for c in e.world["characters"]], ["char_reina"])
        valid_ids = set(e.pages)
        for page in e.world["encounters"]:
            for option in page["options"]:
                self.assertEqual(len(option["reactions"]), 2)
                self.assertEqual({r["consequence_id"] for r in option["reactions"]} <= valid_ids, True)
                self.assertEqual(len({json.dumps(r["after_effects"], sort_keys=True) for r in option["reactions"]}), 1)
                self.assertGreaterEqual(min(len(r["after_effects"]) for r in option["reactions"]), 3)
                self.assertTrue(option["action_id"])

    def test_all_endings_reachable_without_cycles(self):
        reached = set()
        def visit(e, depth=0):
            self.assertLess(depth, 8)
            if e.phase == "DONE":
                reached.add(e.ending)
                return
            for action in e.available_actions():
                next_e = copy.deepcopy(e)
                next_e.step(action)
                visit(next_e, depth + 1)
        visit(Episode())
        terminal = {p["id"] for p in Episode().world["encounters"] if not p["options"]}
        self.assertEqual(reached, terminal)

    def test_dialogue_cannot_change_world(self):
        actions = self.cases[0]["actions"]
        a, b = Episode(), Episode()
        for action in actions:
            a.step(action, dialogue="I dislike you.")
            b.step(action, dialogue="Please stay safe.")
        self.assertEqual(a.flags, b.flags)
        self.assertEqual(a.traits, b.traits)
        self.assertEqual(a.ending, b.ending)

    def test_invalid_action_does_not_advance(self):
        e = Episode()
        with self.assertRaises(ValueError):
            e.step("COMMIT_ANNOUNCE")
        self.assertEqual(e.phase, "S0")
        self.assertEqual(e.trace, [])

    def test_scoring_requires_completed_postlude_and_external_judge(self):
        e = Episode()
        with self.assertRaises(RuntimeError):
            e.result()
        for action in self.cases[0]["actions"]:
            e.step(action)
        self.assertIsNone(e.result()["scores"]["composite"])
        self.assertAlmostEqual(e.result(persona=90, coherence=95)["scores"]["composite"], 96.75)
        with self.assertRaises(ValueError):
            e.result(persona=150, coherence=95)

    def test_phase_clock_gates_follow_nudge_semantics(self):
        e = Episode()
        expected = [
            ("INSPECT_CARD", "S1", 0.30),
            ("VERIFY_DISPATCH", "S2", 0.51),
            ("COMMIT_ANNOUNCE", "S3", 0.657),
            ("ANNOUNCE_MINIMAL", "S4", 0.7599),
        ]
        for action, phase, clock in expected:
            e.step(action)
            self.assertEqual(e.phase, phase)
            self.assertAlmostEqual(e.traits["Phase_Clock"], clock, places=4)
            gate = e.pages[e.node]["acceptability_script"]
            if isinstance(gate, dict):
                self.assertLessEqual(gate["operands"][1]["value"], e.traits["Phase_Clock"])

        short_path = Episode()
        for action in ("INSPECT_CARD", "VERIFY_DISPATCH", "COMMIT_SILENCE"):
            short_path.step(action)
        self.assertEqual(short_path.phase, "S4")
        self.assertAlmostEqual(short_path.traits["Phase_Clock"], 0.657, places=4)
        threshold = short_path.pages[short_path.node]["acceptability_script"]["operands"][1]["value"]
        self.assertLessEqual(threshold, short_path.traits["Phase_Clock"])

    def test_flags_are_monotonic(self):
        for case in self.cases:
            e = Episode()
            previous = {}
            for action in case["actions"]:
                e.step(action)
                for name in ("card_known", "verified", "warned", "public_exposure", "privacy_breach"):
                    if previous.get(name):
                        self.assertTrue(e.flags[name])
                previous = dict(e.flags)

    def test_swmd_has_mcp_contract(self):
        content = (ROOT / "tsun01b.swmd.min.md").read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"))
        for key in ("title:", "storyworld_id:", "state_variables:", "endings:", "expected_critic_score:", "# SWMD-0-MIN"):
            self.assertIn(key, content)
        for page in Episode().pages:
            self.assertIn(f"ENC {page} ", content)


if __name__ == "__main__":
    unittest.main()
