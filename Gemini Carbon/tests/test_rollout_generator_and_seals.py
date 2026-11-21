"""Unit tests for rollout generator rungs, seed firewall, zero leakage, and gym stepping."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from pathlib import Path
import sys
import unittest

CARBON_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CARBON_DIR / "src"))

from carbon_hypergames.cognitive_policies import (  # noqa: E402
    run_budgeted_deliberation_policy,
    run_public_filtration_policy,
    score_rollout_prediction,
)
from carbon_hypergames.rollout_generator import (  # noqa: E402
    HypergameRolloutEnv,
    RUNG_SPECS,
    generate_episode,
    sample_exogenous_root,
    to_public_task_record,
    to_sealed_label_record,
)


class TestRolloutGeneratorAndSeals(unittest.TestCase):
    def test_sealed_confirm_namespace_refuses_unsealed_access(self) -> None:
        with self.assertRaises(PermissionError):
            sample_exogenous_root("sealed_confirm", 0)
        unsealed = sample_exogenous_root("sealed_confirm", 0, allow_unseal_confirm=True)
        train_r = sample_exogenous_root("train", 0)
        dev_r = sample_exogenous_root("dev_pilot", 0)
        self.assertEqual(len({unsealed.root_id, train_r.root_id, dev_r.root_id}), 3)

    def test_public_task_has_zero_arm_or_unobserved_latent_leakage(self) -> None:
        root = sample_exogenous_root("dev_pilot", 5)
        ep_nom = generate_episode(root, "R3_p2_xor_coalition", arm_variant="nominal")
        ep_sham = generate_episode(root, "R3_p2_xor_coalition", arm_variant="matched_sham")
        pub_nom = to_public_task_record(ep_nom)
        pub_sham = to_public_task_record(ep_sham)

        self.assertNotIn("nominal", str(pub_nom["prompt"]))
        self.assertNotIn("matched_sham", str(pub_sham["prompt"]))
        self.assertNotIn("do_intervention", str(pub_nom["prompt"]))
        self.assertNotIn("optimal_action", pub_nom)
        self.assertNotIn("true_target_bit", pub_nom)

        # Flipping an unobserved assembly coordinate (bit 6) leaves public observations unchanged!
        flipped_root = replace(root, latent_world=root.latent_world ^ (1 << 6))
        ep_flipped = generate_episode(flipped_root, "R3_p2_xor_coalition", arm_variant="nominal")
        self.assertEqual(
            to_public_task_record(ep_nom)["public_observations"],
            to_public_task_record(ep_flipped)["public_observations"],
        )

    def test_public_only_p4_matches_exact_grader_posterior_and_sham_invariance(self) -> None:
        for r_idx in range(8):
            root = sample_exogenous_root("dev_pilot", r_idx)
            for rung in RUNG_SPECS:
                rid = str(rung["rung_id"])
                ep_nom = generate_episode(root, rid, arm_variant="nominal")
                ep_sham = generate_episode(root, rid, arm_variant="matched_sham")
                t_nom = to_public_task_record(ep_nom)
                t_sham = to_public_task_record(ep_sham)
                l_nom = to_sealed_label_record(ep_nom)

                pred_nom = run_public_filtration_policy(t_nom, "P4_exact_full_bayes")
                pred_sham = run_public_filtration_policy(t_sham, "P4_exact_full_bayes")
                self.assertEqual(pred_nom["belief_probability"], l_nom["exact_target_probability"])
                self.assertEqual(pred_nom["action"], l_nom["optimal_action"])
                # Tensor-product conditional independence: orthogonal sham leaves focal belief invariant!
                self.assertEqual(pred_nom["belief_probability"], pred_sham["belief_probability"])
                self.assertEqual(pred_nom["action"], pred_sham["action"])

    def test_budget_ladder_monotonicity_across_depths(self) -> None:
        # Across 16 roots x 5 rungs, increasing budget 0 -> 64 -> 256 -> 512 -> 1536 must be non-decreasing!
        totals = {b: 0 for b in (0, 64, 256, 512, 1536)}
        for r_idx in range(16):
            root = sample_exogenous_root("dev_pilot", r_idx)
            for rung in RUNG_SPECS:
                ep = generate_episode(root, str(rung["rung_id"]))
                t = to_public_task_record(ep)
                lbl = to_sealed_label_record(ep)
                for b in totals:
                    sc = score_rollout_prediction(run_budgeted_deliberation_policy(t, b), lbl)
                    totals[b] += int(sc["score"])
        self.assertLess(totals[0], totals[64])
        self.assertLess(totals[64], totals[256])
        self.assertLess(totals[256], totals[512])
        self.assertLess(totals[512], totals[1536])
        self.assertEqual(totals[1536], 16 * 5)

    def test_interactive_gym_and_critical_action_gate(self) -> None:
        env = HypergameRolloutEnv(split="train", world_id="the_glass_concordat")
        obs = env.reset(root_index=2, rung_id="R4_delayed_revision_causal_twin")
        self.assertEqual(obs["turn"], 1)
        for expected_turn in range(2, 6):
            obs, rew, done, _ = env.step("CONTINUE_DELIBERATION")
            self.assertFalse(done)
            self.assertEqual(rew, 0.0)
            self.assertEqual(obs["turn"], expected_turn)

        # Terminal step with trap critical action `FORCE_UNILATERAL_LOCK`
        obs, rew, done, info = env.step("FORCE_UNILATERAL_LOCK", Fraction(3, 4))
        self.assertTrue(done)
        self.assertEqual(info["critical_action"], 1)
        self.assertEqual(info["legal_action"], 0)
        self.assertEqual(info["task_success"], 0)
        self.assertLess(rew, 0.0)
        self.assertEqual(len(info["manifold_vector_24d"]), 24)
        self.assertEqual(len(info["step_logs"]), 5)
        kr_p1 = info["step_logs"][0]["reasoning_interpret_log"]["cited_pvalue_keyrings"][0]
        kr_p2 = info["step_logs"][0]["reasoning_interpret_log"]["cited_p2value_keyrings"][0]
        self.assertEqual(len(kr_p1), 2)
        self.assertEqual(len(kr_p2), 3)


if __name__ == "__main__":
    unittest.main()
