"""HGW-05 exact causal, p2, source and independent-root guard tests."""
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from hgw05_causal_families import (
    FAMILIES, _posterior, _prior, _pair_moment, _marginal, _trial_posterior,
    generate_case, observational_law, policy_result, run_development, public_task, export_development_tasks,
)


class CausalFamilyTests(unittest.TestCase):
    def test_observational_twins_share_law_and_interventions_diverge(self):
        law = observational_law()
        self.assertEqual(law["direct_equal"], law["confounded_equal"])
        self.assertEqual(law["direct_equal"], Q(25,32))
        self.assertEqual(law["direct_ate"], Q(9,16))
        self.assertEqual(law["confounded_ate"], 0)
        for i in range(15):
            d = generate_case("direct", "matched-root", i)
            c = generate_case("confounded", "matched-root", i)
            self.assertEqual(d["public"]["observational_equal"], c["public"]["observational_equal"])
            self.assertEqual(d["public"]["task_type"], c["public"]["task_type"])
            self.assertNotIn("mechanism", str(d["public"]))
            self.assertNotIn("mechanism", str(c["public"]))
            self.assertNotEqual(d["grader"]["optimal_action"], c["grader"]["optimal_action"])
            self.assertTrue(0 <= _trial_posterior(d["public"]) <= 1)

    def test_inferred_second_order_belief_changes_while_p1_stays_fixed(self):
        seen = set()
        for i in range(16):
            case = generate_case("p2_parity", "test-root", i)
            pub = case["public"]
            posterior = _posterior(_prior(), [pub["report"]])
            self.assertEqual(_marginal(posterior, 0), Q(1,2))
            self.assertEqual(_marginal(posterior, 1), Q(1,2))
            moment = _pair_moment(posterior)
            self.assertIn(moment, (Q(1,2), Q(-1,2)))
            seen.add(moment)
            self.assertNotIn("second_order_pair_moment", pub)
            for arm in ("candidate", "baseline", "sham"):
                scored = policy_result(case, arm)
                total = sum(map(Q, scored["inclination_scores"]))
                self.assertEqual(total, 1)
                self.assertTrue(all(Q(16,100) <= v <= Q(84,100) for v in map(Q,scored["inclination_scores"])))
        self.assertEqual(seen, {Q(1,2),Q(-1,2)})

    def test_source_root_deduplication_exact_and_trusted_audit(self):
        seen_effect = False
        for i in range(20):
            c = generate_case("provenance", "root-p", i)
            reports = c["public"]["reports"]
            original = _posterior(_prior(), reports[:1])
            repeated = _posterior(_prior(), reports[:3])
            self.assertEqual(original, repeated)
            naive = _posterior(_prior(), reports[:3], naive_replays=True)
            self.assertNotEqual(original, naive)
            if len(reports) > 3:
                seen_effect = seen_effect or _posterior(_prior(), reports) != repeated
            self.assertEqual(policy_result(c, "candidate")["task_success"], 1)
            self.assertNotIn("observed_truth", c["public"])
        self.assertTrue(seen_effect)

    def test_development_root_cluster_and_exact_replay(self):
        report = run_development(roots=8,cases_per_root=4)
        self.assertEqual(report, run_development(roots=8,cases_per_root=4))
        self.assertEqual(report["total_case_rows"], 8*4*len(FAMILIES))
        self.assertEqual(report["total_independent_development_roots"], 8*3)
        self.assertEqual(report["generator_roster"]["confirmation_roots_generated"], 0)
        self.assertEqual(len(report["rows_sha256"]), 64)
        self.assertEqual(len(report["primary_causal_twin_evalmath_pilot"]["pilot"]),8)
        self.assertEqual(report["primary_causal_twin_evalmath_pilot"]["measurement_resolution"],"1/8")
        for f in FAMILIES:
            r=report["families"][f]
            self.assertEqual(r["independent_development_roots"],8)
            self.assertEqual(r["evalmath_pilot"]["heldout_sealed"],False)
            self.assertEqual(r["evalmath_pilot"]["units_independent"],True)
            self.assertEqual(len(r["evalmath_pilot"]["pilot"]),8)
            self.assertTrue(all(row["sham_effects"] == ["0"] for row in r["evalmath_pilot"]["pilot"]))
            self.assertLessEqual(r["candidate_first_preference"], 32)

    def test_public_prompts_contain_no_private_generator_labels(self):
        from tempfile import TemporaryDirectory
        for family in FAMILIES:
            c=generate_case(family,"root",0)
            task=public_task(c)
            self.assertEqual(task["schema"],"hgw05/causal-families/v1")
            self.assertIn("belief_probability",task["prompt"])
            self.assertNotIn("observed_truth",str(task))
            self.assertNotIn("optimal_action",str(task))
            if family in ("direct","confounded"):
                self.assertNotIn(family, task["task_id"])
        with TemporaryDirectory() as td:
            f=Path(td)/"public.jsonl"
            export_development_tasks(f,roots=2,cases_per_root=2)
            import json
            lines=[json.loads(x) for x in f.read_text().splitlines()]
            self.assertEqual(len(lines),len(FAMILIES)*4)
            self.assertTrue(all("grader" not in x for x in lines))

    def test_bad_root_and_family_errors(self):
        with self.assertRaises(ValueError):generate_case("latent_leak","r",0)
        with self.assertRaises(ValueError):generate_case("direct","r",-1)
        with self.assertRaises(ValueError):run_development(roots=1)

if __name__ == "__main__":
    unittest.main()
