"""Re-evaluate the unmodified HG-07 source-locked public six-seed receipts."""
from __future__ import annotations

import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from fsi01_hg07_seed_audit import audit, REG, CSV


class HG07FSITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=audit()

    def test_source_bound_and_full_census(self):
        a=self.a
        self.assertEqual(a["census"]["neural_fits"],360)
        self.assertEqual(a["census"]["independent_seed_worlds"],6)
        self.assertEqual(a["source_sha256"]["seed_csv"],
                         "053417219cc189208317823d5d944e5a9cc17c3eb0b50810986cdfcff933c81a")
        self.assertEqual(a["census"]["per_seed_test_states"],256)

    def test_h1_fails_and_exact_seed_signflips(self):
        h=self.a["H1"]
        self.assertEqual(h["seed_differences_correct_per_256"],[-1,22,-1,0,-8,6])
        self.assertEqual((h["positive_seed_count"],h["negative_seed_count"],h["tie_seed_count"]),(2,3,1))
        self.assertFalse(h["registered_directional_gate"])
        self.assertEqual(Q(h["seed_signflip_p_exact"]),Q(3,4))
        self.assertEqual(Q(h["holm_exact"]),Q(3,4))

    def test_h2_gate_is_weak_and_not_a_significance_test(self):
        h=self.a["H2"]
        self.assertEqual(h["seed_differences_correct_per_256"],[4,4,4,25,0,-4])
        self.assertTrue(h["registered_directional_gate"])
        self.assertEqual(Q(h["macro_effect_exact"]),Q(33,1536))
        self.assertEqual(Q(h["seed_signflip_p_exact"]),Q(5,16))
        self.assertEqual(Q(h["holm_exact"]),Q(5,8))
        self.assertEqual(h["inference_verdict"],"inconclusive_six_seeds")

    def test_h3_equivalence_is_not_certified(self):
        h3=self.a["H3"]
        self.assertEqual(len(h3),5)
        self.assertEqual({k:v["within_five_pp_seeds"] for k,v in h3.items()},
            {"linear_task":5,"flat_task":4,"loop_task":5,
             "loop_true_fragment_aux":5,"loop_shuffled_fragment_aux":5})
        self.assertTrue(all(x["registered_gate"] for x in h3.values()))
        self.assertTrue(all(not x["equivalence_established"] for x in h3.values()))

    def test_exact_structural_prior_and_calibration_failure(self):
        self.assertTrue(self.a["H4"]["holds_on_registered_census"])
        self.assertEqual(self.a["H4"]["independent_generator_worlds"],36)
        self.assertEqual(self.a["H4"]["matched_test_outcomes"],9216)
        releases=self.a["release_failures"]
        self.assertEqual(len(releases),1)
        self.assertEqual(releases[0]["direct_cal_correct"],155)
        self.assertEqual(releases[0]["direct_test_correct"],129)
        self.assertEqual(releases[0]["direct_false_accept"],127)
        self.assertEqual(releases[0]["direct_true_utility"],"-615/256")

    def test_does_not_require_private_seeds(self):
        self.assertNotIn("private", str(REG).lower())
        self.assertNotIn("private", str(CSV).lower())


if __name__=="__main__":
    unittest.main()
