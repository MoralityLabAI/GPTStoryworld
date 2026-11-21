"""Tests for EvalMath preflight, FSI-01 manifests, budget tables, and cross-repo parity."""

from __future__ import annotations

import os
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
from carbon_hypergames.evalmath_bridge import (  # noqa: E402
    build_budget_sweep_tables,
    build_evalmath_fsi01_manifest,
    build_evalmath_preflight_spec,
    verify_against_evalmath_repo,
)
from carbon_hypergames.rollout_generator import (  # noqa: E402
    RUNG_SPECS,
    generate_episode,
    sample_exogenous_root,
    to_public_task_record,
    to_sealed_label_record,
)


def _locate_evalmath_repo() -> Path | None:
    env_path = os.environ.get("EVALMATH_ROOT")
    if env_path and Path(env_path).is_dir():
        return Path(env_path)
    candidates = [
        CARBON_DIR.parents[1] / "EvalMath",
        CARBON_DIR.parent / "evalmath_pinned",
    ]
    for c in candidates:
        if (c / "skills" / "evalmath-mechinterp-power" / "scripts" / "preflight.py").is_file():
            return c
    return None


class TestEvalMathInteroperability(unittest.TestCase):
    def test_64root_preflight_fsi01_and_budget_tables(self) -> None:
        cand_nom, base_nom, cand_sham = [], [], []
        cond_runs = {}
        budgets = (0, 64, 256, 512, 1536)
        b_rollouts = {b: [] for b in budgets}
        b_scores = {b: [] for b in budgets}

        for r_idx in range(64):
            root = sample_exogenous_root("dev_pilot", r_idx)
            for rung in RUNG_SPECS:
                rid = str(rung["rung_id"])
                ep_nom = generate_episode(root, rid, arm_variant="nominal")
                ep_sham = generate_episode(root, rid, arm_variant="matched_sham")
                t_nom = to_public_task_record(ep_nom)
                l_nom = to_sealed_label_record(ep_nom)
                t_sham = to_public_task_record(ep_sham)
                l_sham = to_sealed_label_record(ep_sham)

                cand_nom.append(score_rollout_prediction(run_public_filtration_policy(t_nom, "P4_exact_full_bayes"), l_nom))
                base_nom.append(score_rollout_prediction(run_public_filtration_policy(t_nom, "P1_first_order_relay_naive"), l_nom))
                cand_sham.append(score_rollout_prediction(run_public_filtration_policy(t_sham, "P4_exact_full_bayes"), l_sham))

                for b in budgets:
                    rb = run_budgeted_deliberation_policy(t_nom, b)
                    b_rollouts[b].append(rb)
                    b_scores[b].append(score_rollout_prediction(rb, l_nom))

        for b in budgets:
            cond_runs[f"b{b}"] = {"model": "ref", "budget": b, "rollouts": b_rollouts[b], "scores": b_scores[b]}
        bt = build_budget_sweep_tables(condition_runs=cond_runs)
        self.assertEqual(bt["depths"], [1, 2, 4, 8, 12])
        staircase = [s["smallest_budget"] for s in bt["smallest_budget_reaching_target"]]
        self.assertEqual(staircase, [0, 64, 256, 512, 1536])

        pf_spec = build_evalmath_preflight_spec(
            experiment_id="TEST-DEV64",
            candidate_nominal_scores=cand_nom,
            baseline_nominal_scores=base_nom,
            candidate_sham_scores=cand_sham,
            heldout_sealed=False,
        )
        self.assertEqual(len(pf_spec["pilot"]), 64)

        fsi_manifest = build_evalmath_fsi01_manifest(
            experiment_id="TEST-FSI-DEV64",
            target_population="dev64",
            candidate_scores=cand_nom,
            baseline_scores=base_nom,
            sealed_readout=False,
        )
        self.assertEqual(len(fsi_manifest["cases"]), 320)

        em_root = _locate_evalmath_repo()
        if em_root is not None:
            receipt = verify_against_evalmath_repo(
                evalmath_root=em_root,
                preflight_spec=pf_spec,
                fsi01_manifests={"primary": fsi_manifest},
            )
            self.assertTrue(all(receipt["parity_checks"].values()))
            pf_res = receipt["preflight_result"]
            self.assertEqual(pf_res["decision"], "REDESIGN_OR_PILOT_ONLY")
            self.assertEqual(pf_res["reasons"], ["heldout_unsealed"])
            self.assertEqual(pf_res["upper_sham_quantile"], 0.0)
            self.assertIsNotNone(pf_res["order_statistic_rank"])
            self.assertLessEqual(pf_res["approx_worlds_for_80pct_power"], 128)


if __name__ == "__main__":
    unittest.main()
