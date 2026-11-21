# AGENTS.md — Gemini Carbon Hypergame Storyworlds & Variable-Reasoning Rollouts

## Scope & Rules
This directory (`Gemini Carbon/`) houses playable SweepWeave 0.1.9 hypergame storyworlds paired with an exact `2^10 = 1,024`-microstate rational filtration and variable-reasoning rollout generator integrated with `MoralityLabAI/EvalMath`.

Before adding new hypergame tasks, changing reaction mathematics, or running model evaluations:
1. Read [`skills/variable-reasoning-hypergame-rollouts/SKILL.md`](skills/variable-reasoning-hypergame-rollouts/SKILL.md) and its references.
2. Read the upstream `EvalMath` [`evalmath-mechinterp-power`](https://github.com/MoralityLabAI/EvalMath/tree/main/skills/evalmath-mechinterp-power) contract.

## Non-Negotiable Scientific & Engineering Invariants
- **Independent Unit:** `cluster_id = root_id` (exogenous generator root). Never count rungs (`R1..R5`), turns (`1..5`), budgets (`0..1536`), or `1,024` posterior states within one root as extra independent worlds.
- **Seed-Namespace Firewall:** Keep `CARBON-TRAIN-HYPERGAME-v1`, `CARBON-DEV-PILOT-HYPERGAME-v1` (>= 64 roots for 95/95 sham calibration), and `CARBON-SEALED-CONFIRM-HYPERGAME-v1` (128 planned untouched roots) strictly separated. Never pass `allow_unseal_confirm=True` until model checkpoints, prompts, and neural sham calibrations are frozen.
- **Algorithmic Ceilings vs Neural Claims:** Reference policies (`P0..P4`, `budget_ref_b*`) are programmatic filtration ceilings/ablations operating on `tasks.jsonl`, never neural model results.
- **SweepWeave Validation:** Every `storyworld.json` edit must pass `codex-skills/storyworld-building/scripts/sweepweave_validator.py`, `storyworld_quality_gate.py --strict` (28/28 checks), and `monte_carlo_rehearsal.py` (`0` dead ends, `>5%` secret reachability) with `PYTHONIOENCODING=utf-8`.
- **No Local Paths or Secrets:** Scrub local paths before committing JSON/Markdown reports.
