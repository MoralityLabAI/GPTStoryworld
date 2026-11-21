#!/usr/bin/env python3
"""Run filtration ladder, budget sweep, and cross-repo EvalMath verification."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Dict, List, Mapping

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
    render_budget_sweep_markdown,
    verify_against_evalmath_repo,
)


def _read_jsonl(path: Path) -> List[Dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_audit(datasets_dir: Path, evalmath_root: Path, out_dir: Path) -> Dict[str, object]:
    dev_dir = datasets_dir / "dev_pilot_64x5"
    nom_tasks = _read_jsonl(dev_dir / "nominal_tasks.jsonl")
    nom_labels = {r["task_id"]: r for r in _read_jsonl(dev_dir / "nominal_labels.jsonl")}
    do_tasks = _read_jsonl(dev_dir / "do_intervention_tasks.jsonl")
    do_labels = {r["task_id"]: r for r in _read_jsonl(dev_dir / "do_intervention_labels.jsonl")}
    sham_tasks = _read_jsonl(dev_dir / "matched_sham_tasks.jsonl")
    sham_labels = {r["task_id"]: r for r in _read_jsonl(dev_dir / "matched_sham_labels.jsonl")}

    # 1. Evaluate all 5 canonical epistemic filtrations (`P0`..`P4`) on public tasks ONLY
    policy_names = (
        "P0_prior_only",
        "P1_first_order_relay_naive",
        "P2_dedup_first_order",
        "P3_p2_stale_depth4",
        "P4_exact_full_bayes",
    )
    filtration_scores: Dict[str, List[Dict[str, object]]] = {}
    filtration_rung_table: Dict[str, Dict[str, Dict[str, float]]] = {}

    for pname in policy_names:
        scored_rows: List[Dict[str, object]] = []
        by_rung: Dict[str, List[Dict[str, object]]] = defaultdict(list)
        for task in nom_tasks:
            pred = run_public_filtration_policy(task, pname)
            srow = score_rollout_prediction(pred, nom_labels[str(task["task_id"])])
            scored_rows.append(srow)
            by_rung[str(srow["rung_id"])].append(srow)
        filtration_scores[pname] = scored_rows
        filtration_rung_table[pname] = {
            rung_id: {
                "accuracy": round(sum(int(x["score"]) for x in rows) / len(rows), 4),
                "mean_brier": round(sum(float(x["brier_float"]) for x in rows) / len(rows), 4),
                "mean_excess_brier": round(
                    sum(float(x["excess_brier_float"]) for x in rows) / len(rows), 4
                ),
            }
            for rung_id, rows in sorted(by_rung.items())
        }

    # Evaluate P4 on `matched_sham` and `do_intervention` to measure causal responsiveness vs sham invariance
    p4_sham_scores = [
        score_rollout_prediction(
            run_public_filtration_policy(t, "P4_exact_full_bayes"),
            sham_labels[str(t["task_id"])],
        )
        for t in sham_tasks
    ]
    p4_do_preds = {
        ( nom_labels_or_do := do_labels[str(t["task_id"])] )["root_id"] + "::" + str(nom_labels_or_do["rung_id"]):
        run_public_filtration_policy(t, "P4_exact_full_bayes")["action"]
        for t in do_tasks
    }
    p4_nom_preds = {
        nom_labels[str(t["task_id"])]["root_id"] + "::" + str(nom_labels[str(t["task_id"])]["rung_id"]):
        run_public_filtration_policy(t, "P4_exact_full_bayes")["action"]
        for t in nom_tasks
    }
    p4_sham_preds = {
        sham_labels[str(t["task_id"])]["root_id"] + "::" + str(sham_labels[str(t["task_id"])]["rung_id"]):
        run_public_filtration_policy(t, "P4_exact_full_bayes")["action"]
        for t in sham_tasks
    }
    do_action_flip_rate = round(
        sum(1 for k in p4_nom_preds if p4_do_preds[k] != p4_nom_preds[k]) / len(p4_nom_preds),
        4,
    )
    sham_action_flip_rate = round(
        sum(1 for k in p4_nom_preds if p4_sham_preds[k] != p4_nom_preds[k]) / len(p4_nom_preds),
        4,
    )

    # 2. Evaluate 5-budget reasoning sweep (`B in {0, 64, 256, 512, 1536}`) across depths {1, 2, 4, 8, 12}
    budgets = (0, 64, 256, 512, 1536)
    condition_runs: Dict[str, Mapping[str, object]] = {}
    for b in budgets:
        rollouts_b: List[Dict[str, object]] = []
        scores_b: List[Dict[str, object]] = []
        for task in nom_tasks:
            pred = run_budgeted_deliberation_policy(task, budget_tokens=b)
            srow = score_rollout_prediction(pred, nom_labels[str(task["task_id"])])
            rollouts_b.append(pred)
            scores_b.append(srow)
        condition_runs[f"carbon-filtration-ref-b{b}"] = {
            "model": "carbon-filtration-ref (algorithmic ceiling)",
            "budget": b,
            "rollouts": rollouts_b,
            "scores": scores_b,
        }

    budget_tables = build_budget_sweep_tables(condition_runs=condition_runs, target_accuracy=0.80)
    budget_md = render_budget_sweep_markdown(budget_tables)

    # 3. Build EvalMath preflight spec (64 independent dev roots, heldout_sealed=False)
    preflight_spec = build_evalmath_preflight_spec(
        experiment_id="CARBON-HG-VAR-REASONING-DEV64",
        candidate_nominal_scores=filtration_scores["P4_exact_full_bayes"],
        baseline_nominal_scores=filtration_scores["P1_first_order_relay_naive"],
        candidate_sham_scores=p4_sham_scores,
        planned_comparisons=5,
        confirm_units_planned=128,
        alpha="0.05",
        scientific_min_effect="0.10",
        target_effect="0.25",
        measurement_resolution="0.05",
        pilot_from_development_only=True,
        heldout_sealed=False,
        units_independent=True,
    )

    # 4. Build 5 registered root-clustered FSI-01 manifests (development-only, `sealed_readout=False`)
    fsi_manifests: Dict[str, Dict[str, object]] = {
        "C1_full_bayes_vs_relay_naive_all_rungs": build_evalmath_fsi01_manifest(
            experiment_id="C1_full_bayes_vs_relay_naive_all_rungs",
            target_population="64 independent development roots across 3 storyworlds x 5 rungs",
            candidate_scores=filtration_scores["P4_exact_full_bayes"],
            baseline_scores=filtration_scores["P1_first_order_relay_naive"],
            planned_comparisons=5,
            sealed_readout=False,
        ),
        "C2_dedup_vs_relay_naive_R2": build_evalmath_fsi01_manifest(
            experiment_id="C2_dedup_vs_relay_naive_R2",
            target_population="64 independent development roots on R2 provenance-deduplication rung",
            candidate_scores=[r for r in filtration_scores["P2_dedup_first_order"] if r["rung_id"] == "R2_provenance_dedup"],
            baseline_scores=[r for r in filtration_scores["P1_first_order_relay_naive"] if r["rung_id"] == "R2_provenance_dedup"],
            planned_comparisons=5,
            sealed_readout=False,
        ),
        "C3_p2_parity_vs_first_order_R3": build_evalmath_fsi01_manifest(
            experiment_id="C3_p2_parity_vs_first_order_R3",
            target_population="64 independent development roots on R3 second-order XOR parity rung",
            candidate_scores=[r for r in filtration_scores["P3_p2_stale_depth4"] if r["rung_id"] == "R3_p2_xor_coalition"],
            baseline_scores=[r for r in filtration_scores["P2_dedup_first_order"] if r["rung_id"] == "R3_p2_xor_coalition"],
            planned_comparisons=5,
            sealed_readout=False,
        ),
        "C4_revision_causal_vs_stale_R4": build_evalmath_fsi01_manifest(
            experiment_id="C4_revision_causal_vs_stale_R4",
            target_population="64 independent development roots on R4 delayed-revision + causal-twin rung",
            candidate_scores=[r for r in filtration_scores["P4_exact_full_bayes"] if r["rung_id"] == "R4_delayed_revision_causal_twin"],
            baseline_scores=[r for r in filtration_scores["P3_p2_stale_depth4"] if r["rung_id"] == "R4_delayed_revision_causal_twin"],
            planned_comparisons=5,
            sealed_readout=False,
        ),
        "C5_12hop_hyperedge_vs_depth4_R5": build_evalmath_fsi01_manifest(
            experiment_id="C5_12hop_hyperedge_vs_depth4_R5",
            target_population="64 independent development roots on R5 12-hop hyperedge + recall rung",
            candidate_scores=[r for r in filtration_scores["P4_exact_full_bayes"] if r["rung_id"] == "R5_multihop_hyperedge_cascade"],
            baseline_scores=[r for r in filtration_scores["P3_p2_stale_depth4"] if r["rung_id"] == "R5_multihop_hyperedge_cascade"],
            planned_comparisons=5,
            sealed_readout=False,
        ),
    }

    # 5. Execute pinned EvalMath repo modules directly!
    evalmath_receipt = verify_against_evalmath_repo(
        evalmath_root=evalmath_root,
        preflight_spec=preflight_spec,
        fsi01_manifests=fsi_manifests,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "evalmath_pilot_spec_64roots.json").write_bytes(
        (json.dumps(preflight_spec, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    (out_dir / "budget_tables.json").write_bytes(
        (json.dumps(budget_tables, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    (out_dir / "budget_tables.md").write_bytes(budget_md.encode("utf-8"))

    full_audit = {
        "schema": "gemini-carbon/hypergame-evalmath-audit/v1",
        "evidence_scope": (
            "Development-only (`heldout_sealed=false`, `sealed_readout=false`) exact finite-filtration "
            "and algorithmic ceiling characterization across 64 independent generator roots. "
            "No neural model generalization is claimed; 128 confirmation roots remain unopened."
        ),
        "causal_vs_sham_selectivity": {
            "do_intervention_action_flip_rate": do_action_flip_rate,
            "matched_sham_action_flip_rate": sham_action_flip_rate,
        },
        "filtration_ladder_by_rung": filtration_rung_table,
        "evalmath_verification": evalmath_receipt,
    }
    (out_dir / "evalmath_verification_receipt.json").write_bytes(
        (json.dumps(full_audit, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    return full_audit


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--datasets-dir", type=Path, default=CARBON_DIR / "datasets")
    ap.add_argument("--evalmath-root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=CARBON_DIR / "reports")
    args = ap.parse_args()

    audit_doc = run_audit(args.datasets_dir, args.evalmath_root, args.out_dir)
    pf = audit_doc["evalmath_verification"]["preflight_result"]
    print(
        json.dumps(
            {
                "preflight_decision": pf["decision"],
                "preflight_reasons": pf["reasons"],
                "pilot_worlds": pf["pilot_worlds"],
                "mean_pilot_effect": pf["mean_pilot_effect"],
                "upper_sham_quantile": pf["upper_sham_quantile"],
                "order_statistic_rank": pf["order_statistic_rank"],
                "approx_worlds_for_80pct_power": pf["approx_worlds_for_80pct_power"],
                "causal_selectivity": audit_doc["causal_vs_sham_selectivity"],
                "parity_checks": audit_doc["evalmath_verification"]["parity_checks"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
