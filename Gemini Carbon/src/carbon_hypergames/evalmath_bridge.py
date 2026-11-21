"""Native interoperability bridge between Gemini Carbon Hypergames and EvalMath.

Connects Hypergame variable-reasoning rollouts directly to:
1. `EvalMath/skills/evalmath-mechinterp-power/scripts/preflight.py`
   (root-clustered power planning, >=59-world nonparametric 95/95 sham envelope,
   discrete exact-sign root floor, zero-variance null guard, unsealed dev gate).
2. `EvalMath/src/spiral_ln/evaluation_finite_sample.py` (FSI-01)
   (paired binary evidence gate with `cluster_id = root_id`, cluster sign-flip,
   cluster bootstrap CI, Bonferroni/Holm familywise alpha, Hoeffding bounds).
3. `EvalMath/src/spiral_ln/evaluation_quotient_information_budget.py` (QI-02)
   (exact KL change-of-measure probe floors for causal-twin discrimination).
4. `EvalMath/research/delayed_revision_reference/bridge.py` (EVAL-REV-01)
   (exact finite-population delayed-revision Brier decomposition parity).
5. `PreferredEvals/gym/budget_sweep.py`
   (accuracy, Wilson 95% CIs, Brier/excess-Brier, and minimum budget per depth).
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .filtrations import (
    minimum_interventional_probes,
    verify_delayed_revision_brier_identity,
)


def _load_module_from_path(module_name: str, file_path: Path):
    if not file_path.is_file():
        raise FileNotFoundError(f"EvalMath module file not found: {file_path}")
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module spec from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_evalmath_preflight_spec(
    *,
    experiment_id: str,
    candidate_nominal_scores: Sequence[Mapping[str, object]],
    baseline_nominal_scores: Sequence[Mapping[str, object]],
    candidate_sham_scores: Sequence[Mapping[str, object]],
    planned_comparisons: int = 5,
    confirm_units_planned: int = 128,
    alpha: str = "0.05",
    scientific_min_effect: str = "0.10",
    target_effect: str = "0.25",
    measurement_resolution: str = "0.05",
    pilot_from_development_only: bool = True,
    heldout_sealed: bool = False,
    units_independent: bool = True,
) -> Dict[str, object]:
    """Build an `EvalMath/mechinterp-power` `schema_version=1` preflight input JSON.

    Aggregates all repeated rungs/turns within a world root onto a single
    `unit_id = root_id` so repeated observations within a root are NEVER counted
    as extra independent worlds.
    """
    cand_by_task = {str(r["task_id"]): int(r["task_success"]) for r in candidate_nominal_scores}
    base_by_task = {str(r["task_id"]): int(r["task_success"]) for r in baseline_nominal_scores}

    # Index nominal vs sham candidate scores by (root_id, rung_id)
    nom_by_root_rung: Dict[Tuple[str, str], int] = {}
    root_diffs: Dict[str, List[Fraction]] = defaultdict(list)

    for row in candidate_nominal_scores:
        tid = str(row["task_id"])
        rid = str(row["root_id"])
        rung_id = str(row["rung_id"])
        c_val = cand_by_task[tid]
        b_val = base_by_task[tid]
        root_diffs[rid].append(Fraction(c_val - b_val, 1))
        nom_by_root_rung[(rid, rung_id)] = c_val

    sham_diffs_by_root: Dict[str, List[Fraction]] = defaultdict(list)
    for srow in candidate_sham_scores:
        rid = str(srow["root_id"])
        rung_id = str(srow["rung_id"])
        nom_val = nom_by_root_rung[(rid, rung_id)]
        sham_val = int(srow["task_success"])
        sham_diffs_by_root[rid].append(Fraction(sham_val - nom_val, 1))

    pilot_rows: List[Dict[str, object]] = []
    for rid in sorted(root_diffs.keys()):
        diffs = root_diffs[rid]
        paired_mean = sum(diffs, Fraction(0, 1)) / len(diffs)
        shams = sham_diffs_by_root.get(rid) or [Fraction(0, 1)]
        pilot_rows.append(
            {
                "unit_id": rid,
                "paired_effect": str(paired_mean),
                "sham_effects": [str(x) for x in shams],
            }
        )

    return {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "independent_unit": "exogenous_storyworld_generator_root",
        "alpha": alpha,
        "scientific_min_effect": scientific_min_effect,
        "target_effect": target_effect,
        "measurement_resolution": measurement_resolution,
        "sham_quantile": "0.95",
        "sham_confidence": "0.95",
        "planned_comparisons": planned_comparisons,
        "confirm_units_planned": confirm_units_planned,
        "pilot_from_development_only": pilot_from_development_only,
        "heldout_sealed": heldout_sealed,
        "units_independent": units_independent,
        "pilot": pilot_rows,
    }


def build_evalmath_fsi01_manifest(
    *,
    experiment_id: str,
    target_population: str,
    candidate_scores: Sequence[Mapping[str, object]],
    baseline_scores: Sequence[Mapping[str, object]],
    planned_comparisons: int = 5,
    alpha: str = "0.05",
    minimum_effect: str = "0.10",
    min_independent_clusters: int = 32,
    hypothesis_preregistered: bool = True,
    sealed_readout: bool = False,
    clusters_independent: bool = True,
    exchangeable_pair_labels: bool = True,
) -> Dict[str, object]:
    """Build an `EvalMath` FSI-01 (`evaluation_finite_sample.py`) paired manifest."""
    base_map = {str(r["task_id"]): int(r["task_success"]) for r in baseline_scores}
    cases: List[Dict[str, object]] = []
    for row in candidate_scores:
        tid = str(row["task_id"])
        if tid not in base_map:
            raise ValueError(f"missing baseline score for task_id {tid}")
        cases.append(
            {
                "case_id": tid,
                "cluster_id": str(row["root_id"]),
                "candidate": int(row["task_success"]),
                "baseline": base_map[tid],
            }
        )
    return {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "target_population": target_population,
        "evaluation_mode": "sampled",
        "alpha": alpha,
        "minimum_effect": minimum_effect,
        "planned_comparisons": planned_comparisons,
        "min_independent_clusters": min_independent_clusters,
        "hypothesis_preregistered": hypothesis_preregistered,
        "sealed_readout": sealed_readout,
        "clusters_independent": clusters_independent,
        "exchangeable_pair_labels": exchangeable_pair_labels,
        "resample_seed": 20261121,
        "bootstrap_resamples": 4096,
        "signflip_simulations": 20000,
        "cases": cases,
    }


def wilson_interval(k: int, n: int, z: float = 1.96) -> Optional[List[float]]:
    if n <= 0:
        return None
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return [round(max(0.0, center - half), 3), round(min(1.0, center + half), 3)]


def build_budget_sweep_tables(
    *,
    condition_runs: Mapping[str, Mapping[str, object]],
    target_accuracy: float = 0.80,
) -> Dict[str, object]:
    """Build `PreferredEvals`-compatible depth-by-budget tables plus Brier metrics.

    `condition_runs` maps `condition_name -> {"model": str, "budget": int, "scores": [...], "rollouts": [...]}`.
    """
    all_depths = sorted(
        {
            int(s["hops"])
            for cond in condition_runs.values()
            for s in cond["scores"]  # type: ignore[index]
        }
    )
    cells: Dict[Tuple[str, int, int], Dict[str, object]] = {}
    rows: List[Dict[str, object]] = []

    for cond_name, cond in condition_runs.items():
        model = str(cond["model"])
        budget = int(cond["budget"])
        rollouts_by_tid = {str(r["task_id"]): r for r in cond["rollouts"]}  # type: ignore[index]
        by_depth: Dict[int, List[Tuple[Mapping[str, object], Mapping[str, object]]]] = defaultdict(list)
        for s in cond["scores"]:  # type: ignore[index]
            tid = str(s["task_id"])
            by_depth[int(s["hops"])].append((s, rollouts_by_tid[tid]))

        for depth in all_depths:
            pairs = by_depth.get(depth, [])
            scored = [p for p in pairs if p[0].get("score") is not None]
            n_scored = len(scored)
            k_correct = sum(int(p[0]["score"]) for p in scored)
            correct_tok_per_hop = [
                int((p[1].get("usage") or {}).get("completion_tokens", 0)) / depth
                for p in scored
                if int(p[0]["score"]) == 1 and (p[1].get("usage") or {}).get("completion_tokens") is not None
            ]
            mean_brier = (
                round(sum(float(p[0]["brier_float"]) for p in scored) / n_scored, 4)
                if n_scored
                else None
            )
            mean_excess_brier = (
                round(sum(float(p[0]["excess_brier_float"]) for p in scored) / n_scored, 4)
                if n_scored
                else None
            )
            cell = {
                "condition": cond_name,
                "model": model,
                "budget": budget,
                "depth": depth,
                "n": len(pairs),
                "scored": n_scored,
                "correct": k_correct,
                "accuracy": round(k_correct / n_scored, 4) if n_scored else None,
                "wilson95": wilson_interval(k_correct, n_scored),
                "mean_brier": mean_brier,
                "mean_excess_brier": mean_excess_brier,
                "infra_errors": sum(1 for p in pairs if p[0].get("status") != "completed"),
                "cap_truncated": sum(1 for p in pairs if p[1].get("finish_reason") == "length"),
                "no_answer": sum(
                    1 for p in pairs if p[0].get("status") == "completed" and not p[0].get("format_valid")
                ),
                "completion_tokens_per_hop_correct": (
                    round(sorted(correct_tok_per_hop)[len(correct_tok_per_hop) // 2], 1)
                    if correct_tok_per_hop
                    else None
                ),
            }
            cells[(model, budget, depth)] = cell
            rows.append(cell)

    smallest: List[Dict[str, object]] = []
    models = sorted({str(c["model"]) for c in condition_runs.values()})
    for model in models:
        budgets = sorted({int(c["budget"]) for c in condition_runs.values() if str(c["model"]) == model})
        for depth in all_depths:
            hit = next(
                (
                    b
                    for b in budgets
                    if (cells.get((model, b, depth)) or {}).get("accuracy") is not None
                    and float(cells[(model, b, depth)]["accuracy"]) >= target_accuracy  # type: ignore[arg-type]
                ),
                None,
            )
            smallest.append(
                {
                    "model": model,
                    "depth": depth,
                    "target": target_accuracy,
                    "smallest_budget": hit,
                }
            )

    return {
        "schema": "preferred-evals/budget-sweep-tables-v1",
        "extension": "carbon-hypergames-excess-brier-v1",
        "depths": all_depths,
        "cells": rows,
        "smallest_budget_reaching_target": smallest,
    }


def render_budget_sweep_markdown(tables_doc: Mapping[str, object]) -> str:
    lines = [
        "| model | budget | depth | correct / scored | accuracy (Wilson 95%) | mean Brier | excess Brier | cap-truncated | tokens/hop (median, correct) |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for c in tables_doc["cells"]:  # type: ignore[index]
        ci = c["wilson95"]
        ci_str = f"{c['accuracy']:.3f} ({ci[0]:.2f}-{ci[1]:.2f})" if ci else "n/a"
        lines.append(
            f"| {c['model']} | {c['budget']} | {c['depth']} | {c['correct']} / {c['scored']} | "
            f"{ci_str} | {c['mean_brier']} | {c['mean_excess_brier']} | "
            f"{c['cap_truncated']} | {c['completion_tokens_per_hop_correct']} |"
        )
    lines.extend(
        [
            "",
            "| model | depth (hops) | smallest budget with accuracy >= 0.80 |",
            "| --- | ---: | ---: |",
        ]
    )
    for s in tables_doc["smallest_budget_reaching_target"]:  # type: ignore[index]
        sb = s["smallest_budget"] if s["smallest_budget"] is not None else "none tested"
        lines.append(f"| {s['model']} | {s['depth']} | {sb} |")
    return "\n".join(lines) + "\n"


def verify_against_evalmath_repo(
    evalmath_root: Path,
    preflight_spec: Mapping[str, object],
    fsi01_manifests: Mapping[str, Mapping[str, object]],
) -> Dict[str, object]:
    """Execute pinned `EvalMath` modules directly and verify exact cross-repo parity."""
    preflight_path = evalmath_root / "skills" / "evalmath-mechinterp-power" / "scripts" / "preflight.py"
    fsi_path = evalmath_root / "src" / "spiral_ln" / "evaluation_finite_sample.py"
    qi_path = evalmath_root / "src" / "spiral_ln" / "evaluation_quotient_information_budget.py"
    rev_path = evalmath_root / "research" / "delayed_revision_reference" / "bridge.py"

    preflight_mod = _load_module_from_path("evalmath_preflight", preflight_path)
    fsi_mod = _load_module_from_path("evalmath_fsi01", fsi_path)
    qi_mod = _load_module_from_path("evalmath_qi02", qi_path)
    rev_mod = _load_module_from_path("evalmath_rev01", rev_path)

    # 1. Run EvalMath mechanistic-resolution preflight
    preflight_result = preflight_mod.preflight(dict(preflight_spec))

    # 2. Run EvalMath FSI-01 on every registered comparison manifest + Holm step-down
    fsi_results: Dict[str, Dict[str, object]] = {}
    raw_p_list: List[Tuple[str, float]] = []
    for name, manifest in fsi01_manifests.items():
        res = fsi_mod.evaluate_manifest(dict(manifest))
        fsi_results[name] = res
        p_unadj = res.get("p_unadjusted")
        raw_p_list.append((name, float(p_unadj) if p_unadj is not None else 1.0))

    # Holm-Bonferroni step-down across the complete registered comparison family
    m_total = len(raw_p_list)
    sorted_p = sorted(raw_p_list, key=lambda kv: kv[1])
    holm_adjusted: Dict[str, float] = {}
    running_max = 0.0
    for rank_idx, (cname, pval) in enumerate(sorted_p):
        adj = min(1.0, pval * (m_total - rank_idx))
        running_max = max(running_max, adj)
        holm_adjusted[cname] = round(running_max, 8)
        fsi_results[cname]["p_holm_family"] = holm_adjusted[cname]

    # 3. Cross-check QI-02 KL probe budget lower bound on causal twins (25/32 vs 1/2)
    carbon_probe = minimum_interventional_probes(
        error_tolerance=Fraction(5, 100),
        p_direct=Fraction(25, 32),
        p_confounded=Fraction(1, 2),
    )
    em_floor_d_vs_c = qi_mod.expected_probe_integer_floor(Fraction(25, 32), Fraction(1, 2), Fraction(5, 100))
    em_floor_c_vs_d = qi_mod.expected_probe_integer_floor(Fraction(1, 2), Fraction(25, 32), Fraction(5, 100))
    em_worst_floor = max(em_floor_d_vs_c, em_floor_c_vs_d)
    if carbon_probe["integer_probe_floor"] != em_worst_floor:
        raise AssertionError(
            f"QI-02 probe floor mismatch: carbon={carbon_probe['integer_probe_floor']} vs EvalMath={em_worst_floor}"
        )

    # 4. Cross-check EVAL-REV-01 exact rational delayed-revision Brier decomposition
    carbon_rev = verify_delayed_revision_brier_identity(n_slots=4, revised_slot=0)
    em_rev = rev_mod.raw_population(4, (0,), 0)
    parity_checks = {
        "full_brier_exact_match": str(em_rev["full_brier"]) == carbon_rev["brier_full_history_bayes"],
        "limited_brier_exact_match": str(em_rev["limited_brier"]) == carbon_rev["brier_count_quotient_bayes"],
        "info_loss_regret_exact_match": str(em_rev["regret"]) == carbon_rev["irreducible_info_loss_term"],
        "pythagorean_zero_residual": bool(carbon_rev["exact_zero_residual"]),
        "qi02_worst_case_probe_floor_match": carbon_probe["integer_probe_floor"] == em_worst_floor,
    }
    if not all(parity_checks.values()):
        raise AssertionError(f"EvalMath cross-repo mathematical parity check failed: {parity_checks}")

    return {
        "schema": "carbon-hypergames/evalmath-verification-receipt/v1",
        "evalmath_source_hashes": {
            "preflight_py_sha256": sha256_file(preflight_path),
            "evaluation_finite_sample_py_sha256": sha256_file(fsi_path),
            "evaluation_quotient_information_budget_py_sha256": sha256_file(qi_path),
            "delayed_revision_bridge_py_sha256": sha256_file(rev_path),
        },
        "parity_checks": parity_checks,
        "qi02_causal_twin_probe_budget": {
            "evalmath_floor_direct_under_null": em_floor_d_vs_c,
            "evalmath_floor_confounded_under_null": em_floor_c_vs_d,
            "worst_case_integer_probe_floor": em_worst_floor,
            "carbon_probe_certificate": carbon_probe,
        },
        "eval_rev01_brier_certificate": carbon_rev,
        "preflight_result": preflight_result,
        "fsi01_comparisons": fsi_results,
    }
