#!/usr/bin/env python3
"""Generate variable-reasoning hypergame rollout datasets and sealed registration."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Dict, List

CARBON_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CARBON_DIR / "src"))

from carbon_hypergames.cognitive_policies import run_public_filtration_policy  # noqa: E402
from carbon_hypergames.rollout_generator import (  # noqa: E402
    RUNG_SPECS,
    SEED_NAMESPACES,
    generate_episode,
    sample_exogenous_root,
    to_public_task_record,
    to_sealed_label_record,
)


def _write_jsonl(path: Path, rows: List[Dict[str, object]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(r, sort_keys=True, ensure_ascii=True) + "\n" for r in rows)
    raw = text.encode("utf-8")
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def generate_datasets(out_root: Path, train_roots: int = 24, dev_roots: int = 64) -> Dict[str, object]:
    if dev_roots < 59:
        raise ValueError(
            "EvalMath 95/95 nonparametric sham tolerance bound requires >= 59 independent dev roots"
        )

    # 1. Training rollout split (`train`: nominal multi-turn rollouts across R1..R5)
    train_tasks: List[Dict[str, object]] = []
    train_labels: List[Dict[str, object]] = []
    train_oracle_rollouts: List[Dict[str, object]] = []

    for r_idx in range(train_roots):
        root = sample_exogenous_root("train", r_idx)
        for rung in RUNG_SPECS:
            ep = generate_episode(root, str(rung["rung_id"]), arm_variant="nominal")
            task_rec = to_public_task_record(ep)
            label_rec = to_sealed_label_record(ep)
            oracle_pred = run_public_filtration_policy(task_rec, "P4_exact_full_bayes")
            train_tasks.append(task_rec)
            train_labels.append(label_rec)
            train_oracle_rollouts.append(
                {
                    "task_id": ep.task_id,
                    "root_id": root.root_id,
                    "world_id": root.world_id,
                    "rung_id": ep.rung_id,
                    "hops": ep.hops,
                    "oracle_action": oracle_pred["action"],
                    "oracle_belief_probability": oracle_pred["belief_probability"],
                    "public_turns": list(ep.public_turns),
                    "step_logs": list(ep.step_logs),
                    "manifold_vector_24d": list(ep.manifold_vector_24d),
                }
            )

    train_dir = out_root / "train_rollouts_24x5"
    train_hashes = {
        "tasks_jsonl_sha256": _write_jsonl(train_dir / "tasks.jsonl", train_tasks),
        "labels_jsonl_sha256": _write_jsonl(train_dir / "labels.jsonl", train_labels),
        "oracle_rollouts_jsonl_sha256": _write_jsonl(
            train_dir / "oracle_rollouts.jsonl", train_oracle_rollouts
        ),
    }

    # 2. Development & sham-calibration split (`dev_pilot`: 64 roots x 5 rungs x 3 causal arms)
    dev_nominal_tasks: List[Dict[str, object]] = []
    dev_nominal_labels: List[Dict[str, object]] = []
    dev_do_tasks: List[Dict[str, object]] = []
    dev_do_labels: List[Dict[str, object]] = []
    dev_sham_tasks: List[Dict[str, object]] = []
    dev_sham_labels: List[Dict[str, object]] = []

    for r_idx in range(dev_roots):
        root = sample_exogenous_root("dev_pilot", r_idx)
        for rung in RUNG_SPECS:
            rid = str(rung["rung_id"])
            ep_nom = generate_episode(root, rid, arm_variant="nominal")
            ep_do = generate_episode(root, rid, arm_variant="do_intervention")
            ep_sham = generate_episode(root, rid, arm_variant="matched_sham")

            dev_nominal_tasks.append(to_public_task_record(ep_nom))
            dev_nominal_labels.append(to_sealed_label_record(ep_nom))

            dev_do_tasks.append(to_public_task_record(ep_do))
            dev_do_labels.append(to_sealed_label_record(ep_do))

            dev_sham_tasks.append(to_public_task_record(ep_sham))
            dev_sham_labels.append(to_sealed_label_record(ep_sham))

    dev_dir = out_root / "dev_pilot_64x5"
    dev_hashes = {
        "nominal_tasks_sha256": _write_jsonl(dev_dir / "nominal_tasks.jsonl", dev_nominal_tasks),
        "nominal_labels_sha256": _write_jsonl(dev_dir / "nominal_labels.jsonl", dev_nominal_labels),
        "do_intervention_tasks_sha256": _write_jsonl(
            dev_dir / "do_intervention_tasks.jsonl", dev_do_tasks
        ),
        "do_intervention_labels_sha256": _write_jsonl(
            dev_dir / "do_intervention_labels.jsonl", dev_do_labels
        ),
        "matched_sham_tasks_sha256": _write_jsonl(dev_dir / "matched_sham_tasks.jsonl", dev_sham_tasks),
        "matched_sham_labels_sha256": _write_jsonl(
            dev_dir / "matched_sham_labels.jsonl", dev_sham_labels
        ),
    }

    # 3. Prospective sealed confirmation registration (ZERO confirmation roots materialized!)
    confirm_reg = {
        "schema": "gemini-carbon/prospective-confirmation-registration/v1",
        "experiment_id": "CARBON-HG-VAR-REASONING-20261121",
        "seed_namespace_commitment_sha256": hashlib.sha256(
            SEED_NAMESPACES["sealed_confirm"].encode("utf-8")
        ).hexdigest(),
        "planned_confirmation_roots": 128,
        "confirmation_roots_generated": 0,
        "heldout_sealed": False,
        "rungs": [r["rung_id"] for r in RUNG_SPECS],
        "depths_hops": [r["hops"] for r in RUNG_SPECS],
        "planned_comparisons": 5,
        "alpha": "0.05",
        "scientific_min_effect": "0.10",
        "target_effect": "0.25",
        "note": (
            "Development-phase registration only (`confirmation_roots_generated == 0`). "
            "Before opening `sealed_confirm` roots for any neural model claim, freeze "
            "model weights, prompt templates, and neural sham calibration on `dev_pilot_64x5`."
        ),
    }
    reg_path = out_root / "sealed_confirm_registration.json"
    reg_bytes = (json.dumps(confirm_reg, indent=2, sort_keys=True) + "\n").encode("utf-8")
    reg_path.write_bytes(reg_bytes)

    manifest = {
        "schema": "gemini-carbon/dataset-manifest/v1",
        "train_split": {
            "relpath": "Gemini Carbon/datasets/train_rollouts_24x5",
            "independent_roots": train_roots,
            "episodes": len(train_tasks),
            "hashes": train_hashes,
        },
        "dev_pilot_split": {
            "relpath": "Gemini Carbon/datasets/dev_pilot_64x5",
            "independent_roots": dev_roots,
            "nominal_episodes": len(dev_nominal_tasks),
            "do_intervention_episodes": len(dev_do_tasks),
            "matched_sham_episodes": len(dev_sham_tasks),
            "total_paired_episodes": len(dev_nominal_tasks) + len(dev_do_tasks) + len(dev_sham_tasks),
            "hashes": dev_hashes,
        },
        "sealed_confirm_registration": {
            "relpath": "Gemini Carbon/datasets/sealed_confirm_registration.json",
            "sha256": hashlib.sha256(reg_bytes).hexdigest(),
            "confirmation_roots_generated": 0,
        },
    }
    manifest_path = out_root / "dataset_manifest.json"
    manifest_path.write_bytes((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-root", type=Path, default=CARBON_DIR / "datasets")
    ap.add_argument("--train-roots", type=int, default=24)
    ap.add_argument("--dev-roots", type=int, default=64)
    args = ap.parse_args()

    res = generate_datasets(args.out_root, train_roots=args.train_roots, dev_roots=args.dev_roots)
    print(json.dumps(res, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
