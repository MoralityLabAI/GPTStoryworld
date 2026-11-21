#!/usr/bin/env python3
"""Compile all three Gemini Carbon SweepWeave storyworlds and run strict QA gates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

CARBON_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CARBON_DIR.parent
sys.path.insert(0, str(CARBON_DIR / "src"))
sys.path.insert(0, str(REPO_ROOT / "codex-skills" / "storyworld-building" / "scripts"))

from carbon_hypergames.storyworld_compiler import write_compiled_world_bundle  # noqa: E402
from carbon_hypergames.worlds_spec import WORLD_SPECS  # noqa: E402
from monte_carlo_rehearsal import run_monte_carlo  # noqa: E402
from storyworld_quality_gate import evaluate_storyworld  # noqa: E402
from sweepweave_validator import validate_storyworld  # noqa: E402


def build_all(out_root: Path, mc_runs: int = 5000, seed: int = 42) -> dict:
    summary = {
        "schema": "gemini-carbon/storyworld-build-summary/v1",
        "mc_runs_per_world": mc_runs,
        "mc_seed": seed,
        "worlds": {},
    }

    for world_id in WORLD_SPECS:
        wdir = out_root / world_id
        paths = write_compiled_world_bundle(world_id, wdir)
        sw_path = paths["storyworld_json"]
        sw_data = json.loads(sw_path.read_text(encoding="utf-8"))

        val_errors = validate_storyworld(str(sw_path))
        if val_errors:
            raise RuntimeError(f"SweepWeave validation failed for {world_id}: {val_errors}")

        q_report = evaluate_storyworld(sw_data, val_errors)
        # Scrub local filesystem path for clean git reproducibility!
        q_report["storyworld"] = f"Gemini Carbon/storyworlds/{world_id}/storyworld.json"
        if not q_report["pass"]:
            raise RuntimeError(
                f"Strict quality gate failed for {world_id}: failures={q_report['failures']}"
            )

        q_path = wdir / "quality_gate.json"
        q_path.write_bytes((json.dumps(q_report, indent=2, sort_keys=True) + "\n").encode("utf-8"))

        mc = run_monte_carlo(sw_data, num_runs=mc_runs, seed=seed)
        total_secret_hits = sum(mc["secret_hits"].values())
        secret_pct = round(100.0 * total_secret_hits / mc_runs, 2)
        if mc["dead_ends"] > 0:
            raise RuntimeError(f"Monte Carlo rehearsal found dead ends in {world_id}: {mc['dead_ends']}")
        if secret_pct <= 5.0:
            raise RuntimeError(
                f"Secret ending reachability {secret_pct}% <= 5.0% target in {world_id}"
            )

        mc_clean = {
            "world_id": world_id,
            "num_runs": mc_runs,
            "seed": seed,
            "dead_ends": mc["dead_ends"],
            "ending_counts": dict(sorted(mc["ending_counts"].items())),
            "secret_hits": dict(sorted(mc["secret_hits"].items())),
            "total_secret_reachability_pct": secret_pct,
        }
        mc_path = wdir / "monte_carlo_summary.json"
        mc_path.write_bytes((json.dumps(mc_clean, indent=2, sort_keys=True) + "\n").encode("utf-8"))

        summary["worlds"][world_id] = {
            "storyworld_relpath": f"Gemini Carbon/storyworlds/{world_id}/storyworld.json",
            "storyworld_sha256": hashlib.sha256(sw_path.read_bytes()).hexdigest(),
            "swmd_min_sha256": hashlib.sha256(paths["swmd_min"].read_bytes()).hexdigest(),
            "validator_errors": 0,
            "quality_gate_pass": q_report["pass"],
            "quality_summary": q_report["summary"],
            "dead_ends": mc["dead_ends"],
            "secret_reachability_pct": secret_pct,
            "ending_counts": mc_clean["ending_counts"],
        }

    index_path = out_root / "storyworlds_index.json"
    index_path.write_bytes((json.dumps(summary, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out-root",
        type=Path,
        default=CARBON_DIR / "storyworlds",
        help="Output directory for compiled Gemini Carbon storyworlds",
    )
    ap.add_argument("--mc-runs", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    res = build_all(args.out_root, mc_runs=args.mc_runs, seed=args.seed)
    print(json.dumps(res, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
