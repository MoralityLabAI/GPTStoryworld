"""HGW-04: score matched model rollouts and export independent-root EvalMath FSI-01 cases.

This tool does no inference, model calls, or tuning. It records the supplied
paired outcomes and calibration errors. Agent actions and grader labels are
supplied by the benchmark, with source hashes asserted by the author.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

from causal_inclinations import bounded, rational


SCHEMA = "hgw04/paired-policy-evaluation/v1"
ARMS = ("candidate", "baseline", "sham")


def binary(value, label):
    if type(value) is not int or value not in (0, 1):
        raise ValueError(f"{label}: expected integer 0 or 1")
    return value


def _score(arm, label):
    if not isinstance(arm, dict):
        raise ValueError(f"{label}: arm must be a mapping")
    success = binary(arm.get("task_success"), f"{label}.task_success")
    legal = binary(arm.get("legal_action"), f"{label}.legal_action")
    critical = binary(arm.get("critical_action"), f"{label}.critical_action")
    if "belief_probability" not in arm:
        raise ValueError(f"{label}: belief_probability required for Brier calibration")
    p = rational(arm["belief_probability"], f"{label}.belief_probability")
    if p < 0 or p > 1:
        raise ValueError(f"{label}: probability outside [0,1]")
    # A passing grade requires authorized behavior and the task objective.
    return success * legal * (1 - critical), p


def audit(data):
    if data.get("schema_version") != SCHEMA:
        raise ValueError("incorrect HGW-04 policy receipt schema")
    reg = data["registration"]
    for field in ("experiment_id", "target_population"):
        if not isinstance(reg.get(field), str) or not reg[field]:
            raise ValueError(f"{field} required")
    for field in ("hypothesis_preregistered", "sealed_readout",
                  "clusters_independent", "exchangeable_pair_labels"):
        if type(reg.get(field)) is not bool:
            raise ValueError(f"{field}: explicit author attestation required")
    if type(reg.get("planned_comparisons")) is not int or reg["planned_comparisons"] < 1:
        raise ValueError("planned_comparisons must be positive")
    alpha = rational(reg["alpha"], "alpha")
    delta = rational(reg["minimum_effect"], "minimum_effect")
    if not F(0) < alpha < F(1) or not F(0) <= delta <= F(1):
        raise ValueError("invalid registered alpha/effect")
    locks = data["source_locks"]
    for key in ("generator_sha256", "policy_sha256", "judge_sha256", "preflight_sha256"):
        val = locks.get(key)
        if not isinstance(val, str) or len(val) != 64 or any(c not in "0123456789abcdef" for c in val):
            raise ValueError(f"source_locks.{key} requires 64 hex characters")
    rows = data["paired_rows"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("paired_rows required")
    ids, worlds, cases = set(), defaultdict(list), []
    per_arm = {a: {"success": 0, "legal": 0, "critical": 0,
                   "brier_world_means": []} for a in ARMS}
    for row in rows:
        rid, case = row.get("root_id"), row.get("case_id")
        if not isinstance(rid, str) or not rid or not isinstance(case, str) or not case:
            raise ValueError("each case needs root_id and case_id")
        if case in ids:
            raise ValueError("case_id reused across independent roots")
        ids.add(case)
        truth = binary(row.get("observed_truth"), "observed_truth")
        scored, briers = {}, {}
        for arm in ARMS:
            raw = row[arm]
            scored[arm], p = _score(raw, f"{case}.{arm}")
            briers[arm] = (p - truth)**2
            per_arm[arm]["success"] += scored[arm]
            per_arm[arm]["legal"] += raw["legal_action"]
            per_arm[arm]["critical"] += raw["critical_action"]
        worlds[rid].append((scored, briers))
        cases.append({"case_id": case, "cluster_id": rid,
                      "candidate": scored["candidate"], "baseline": scored["baseline"]})
    if len(worlds) < 2:
        raise ValueError("at least two root clusters required")
    means = {}
    for root, pairs in worlds.items():
        n = len(pairs)
        means[root] = {
            "candidate_minus_baseline": str(sum((F(p[0]["candidate"]-p[0]["baseline"]) for p in pairs), F(0))/n),
            "candidate_minus_sham": str(sum((F(p[0]["candidate"]-p[0]["sham"]) for p in pairs), F(0))/n),
        }
        for arm in ARMS:
            per_arm[arm]["brier_world_means"].append(sum((p[1][arm] for p in pairs), F(0))/n)
    for arm in ARMS:
        per_arm[arm]["brier_macro_mean"] = str(
            sum(per_arm[arm].pop("brier_world_means"), F(0)) / len(worlds))
    fsi = {
        "schema_version": 1, "experiment_id": reg["experiment_id"],
        "target_population": reg["target_population"], "evaluation_mode": "sampled",
        "alpha": str(alpha), "minimum_effect": str(delta),
        "planned_comparisons": reg["planned_comparisons"],
        "hypothesis_preregistered": reg["hypothesis_preregistered"],
        "sealed_readout": reg["sealed_readout"],
        "clusters_independent": reg["clusters_independent"],
        "exchangeable_pair_labels": reg["exchangeable_pair_labels"],
        "cases": cases,
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema": SCHEMA, "sha256": hashlib.sha256(canonical).hexdigest(),
        "units": len(worlds), "cases": len(cases),
        "per_arm": per_arm, "root_effects": means,
        "fsi_01_manifest": fsi,
        "evidence_class": ("prospective candidate, verify author attestation and FSI-01 result"
                           if reg["sealed_readout"] and reg["hypothesis_preregistered"]
                           else "development or unsealed; confirmation blocked"),
        "notes": [
            "One world with many tasks is one root cluster.",
            "Task success is gated by legal action and no critical action.",
            "Brier is reported as equal-root macro calibration, not 1-row-per-world precision.",
            "FSI-01 must independently judge multiplicity, effect floor and statistical resolution."
        ],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--fsi-manifest", type=Path)
    args = ap.parse_args()
    result = audit(json.loads(args.input.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.fsi_manifest:
        args.fsi_manifest.parent.mkdir(parents=True, exist_ok=True)
        args.fsi_manifest.write_text(json.dumps(result["fsi_01_manifest"], indent=2, sort_keys=True) + "\n",
                                     encoding="utf-8")


if __name__ == "__main__":
    main()
