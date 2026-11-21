"""Offline HGW-04 regression tests; no GPU, no private secrets or held-out reads."""
import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from causal_inclinations import SCHEMA, audit, inclination, public_state


def fixture():
    return json.loads((ROOT / "fixtures" / "hgw04_development_pilot.json").read_text(encoding="utf-8"))


class CausalInclinationTests(unittest.TestCase):
    def test_exact_formula_and_complement(self):
        spec = fixture()
        for world in spec["development_worlds"]:
            public = public_state(spec["model"], world["exogenous"])
            scores = inclination(spec["formula"], public)
            self.assertEqual(sum(scores), F(1))
            self.assertTrue(all(F(16, 100) <= x <= F(84, 100) for x in scores))
            self.assertNotIn("z", public)
            self.assertNotIn("audit", public)

    def test_do_recalculates_mediator_and_reuses_same_root(self):
        spec = fixture()
        e = spec["development_worlds"][0]["exogenous"]
        original = public_state(spec["model"], e)
        changed = public_state(spec["model"], e, {"audit": "1"})
        self.assertEqual(changed["evidence"] - original["evidence"], F(1))
        self.assertEqual(changed["belief_about_belief"] - original["belief_about_belief"],
                         F(1, 2) + e["noise"] * F(1, 4))
        self.assertNotEqual(inclination(spec["formula"], changed),
                            inclination(spec["formula"], original))

    def test_irrelevant_sham_and_l1_budget(self):
        spec = fixture()
        root = spec["development_worlds"][0]["exogenous"]
        original = public_state(spec["model"], root)
        sham = public_state(spec["model"], root, {"sham": "-1"})
        self.assertEqual(inclination(spec["formula"], original),
                         inclination(spec["formula"], sham))
        bad = dict(spec["formula"])
        bad["linear"] = {"evidence": "9/10", "belief_about_belief": "1/2"}
        with self.assertRaisesRegex(ValueError, "budget"):
            inclination(bad, original)

    def test_cycle_and_hidden_variable_leak_rejected(self):
        spec = fixture()
        root = spec["development_worlds"][0]["exogenous"]
        bad = dict(spec["model"])
        bad["nodes"] = [{"name": "x", "linear": {"y": "1"}},
                        {"name": "y", "linear": {"x": "1"}}]
        bad["visible"] = ["x"]
        with self.assertRaisesRegex(ValueError, "cyclic"):
            public_state(bad, root)
        public = public_state(spec["model"], root)
        with self.assertRaisesRegex(ValueError, "hidden"):
            inclination({"linear": {"z": "1/4", "evidence": "1/5"}}, public)
        bad["visible"] = ["z"]
        with self.assertRaisesRegex(ValueError, "visible"):
            public_state(bad, root)

    def test_world_root_independence_and_pilot_scope(self):
        spec = fixture()
        result = audit(spec)
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(result["independent_development_roots"], 8)
        self.assertTrue(result["balance"]["both_responses_observed_on_development_roots"])
        self.assertEqual(result["evalmath_pilot"]["schema_version"], 1)
        self.assertFalse(result["evalmath_pilot"]["heldout_sealed"])
        self.assertFalse(result["evalmath_pilot"]["units_independent"])
        self.assertEqual(len(result["evalmath_pilot"]["pilot"]), 8)
        self.assertEqual(result, audit(spec))
        self.assertTrue(all(row["sham_effects"] == ["0"] for row in result["paired_world_effects"]))
        spec["development_worlds"][1]["unit_id"] = spec["development_worlds"][0]["unit_id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            audit(spec)

    def test_reject_bad_graph_and_registration(self):
        spec = fixture()
        bad = dict(spec["model"])
        bad["nodes"] = [{"name": "bad", "linear": {"z": "2"}}]
        bad["visible"] = ["bad"]
        with self.assertRaisesRegex(ValueError, "budget"):
            public_state(bad, spec["development_worlds"][0]["exogenous"])
        spec["evalmath_registration"]["heldout_sealed"] = "yes"
        with self.assertRaisesRegex(ValueError, "true or false"):
            audit(spec)


if __name__ == "__main__":
    unittest.main()
