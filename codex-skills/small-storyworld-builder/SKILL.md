---
name: small-storyworld-builder
description: Build and benchmark short dialogue-driven storyworlds with small local models (1.5B-3B) using MCP bounded-context cards, SWMD minified format, and deterministic quality gates.
---

# Small Storyworld Builder

## When To Use
- Use for low-VRAM local workflows where full-world prompting is not viable.
- Use for short-form worlds (about 12-30 encounters, 2-4 characters) with encounter-at-a-time revision.
- Use when token economics and reproducible benchmark logs matter.

## Core Contract
- Keep model context at or below 8k tokens equivalent.
- Operate on one encounter block at a time using MCP context cards.
- Treat the model as an operation engine, not a full-world memory store.
- Offload world-scale context (even SWMD-min) to MCP cards/packets; never require full-world prompt loading.
- Keep IDs stable (`enc_*`/`page_*`, `opt_*`, `rxn_*`).
- Always validate JSON structure before and after MCP passes.
- Author in SWMD minified markdown first; export JSON only for editor/playable checks.
- Keep YAML frontmatter at top of SWMD-min with explicit terminal `endings` metadata so evaluators can grade terminal states without replaying full graph traversal.

## Required Inputs
- Base world JSON.
- Target world brief (tone, characters, encounter count).
- Model profile (base model, optional adapter, max output tokens).

## Pipeline
1. Seed world:
`python C:/projects/GPTStoryworld/codex-skills/storyworld-building/scripts/one_shot_factory.py --base <base.json> --out <seed.json> --target-encounters <n> --title "<title>" --about "<about>" --motif "<motif>"`
2. Validate + gate:
`python C:/projects/GPTStoryworld/codex-skills/storyworld-building/scripts/sweepweave_validator.py validate <seed.json>`
`python C:/projects/GPTStoryworld/codex-skills/storyworld-building/scripts/storyworld_quality_gate.py --storyworld <seed.json> --strict --report-out <seed_gate.json>`
3. Export SWMD-min:
`python C:/projects/GPTStoryworld/codex-skills/storyworld-building/scripts/json_to_swmd.py <seed.json> <seed.swmd.min.md> --mode minified`
4. Build encounter index:
`python C:/projects/GPTStoryworld/codex-skills/small-storyworld-builder/scripts/swmd_encounter_index.py --swmd <seed.swmd.min.md> --out-dir <enc_index_dir>`
5. Build derived QLoRA examples (compiler-style transforms):
`python C:/projects/GPTStoryworld/codex-skills/small-storyworld-builder/scripts/swmd_build_qlora_examples.py --swmd-glob "<swmd_glob>" --out-dir <QLoraExamples_dir> --max-total-encounters 120 --examples-per-encounter 10 --val-ratio 0.05`
Default task mix:
- 40% compile
- 25% compression
- 20% repair
- 15% targeted_edit
Schema rule: keep `SWMD-MICRO-0.1` key structure identical across all outputs.
Optional hard-negative expansion to ~2k rows:
`python C:/projects/GPTStoryworld/codex-skills/small-storyworld-builder/scripts/swmd_expand_qlora_hard_negatives.py --in-dir <QLoraExamples_dir> --target-total 2000 --out-prefix aug`
6. MCP phased loop (recommended sequence):
- `plan`
- `characterize`
- `encounter_build`
- `act_complete`
- `recharacterize`
- `late_stage_holistic`
- Use `C:/projects/GPTStoryworld/codex-skills/small-storyworld-builder/scripts/swmd_mcp_phase_pipeline.py` with 8k budgeted packets.

Command:
`python C:/projects/GPTStoryworld/codex-skills/small-storyworld-builder/scripts/swmd_mcp_phase_pipeline.py --swmd <seed.swmd.min.md> --model-path D:/Research_Engine/Qwen_Storyworld/cache/models/Qwen3-1.7B --adapter-path <adapter_or_empty> --max-encounters 20 --context-budget-tokens 8192 --reserve-output-tokens 1024 --planning-card-tokens 900 --max-new-tokens 220 --temperature 0 --qlora-examples-jsonl <QLoraExamples_dir/aug_train.jsonl> --fewshot-count 1 --out-jsonl <phase_events.jsonl> --state-json <phase_state.json> --apply`
7. Re-score:
`python C:/projects/GPTStoryworld/storyworld-env/quality_vector_score.py --storyworlds <world.json> --runs 120 --out <vector.json>`
`python C:/projects/GPTStoryworld/storyworld-text-quality-env/evaluate_text_quality.py --storyworld <world.json> --judge-model gpt-4.1-mini --out <text.json>`
For Casablanca and similar moral-crucible benchmarks, include `expected_critic_score` per ending in SWMD frontmatter and compare against critic welfare output.

## Phase Output Discipline
- `plan`, `characterize`, `act_complete`, `recharacterize` must emit compact JSON objects (no prose wrappers).
- `encounter_build` and `late_stage_holistic` must emit one valid SWMD encounter block only.
- For holistic pass under small context windows, use chunk-aware mode and summarize from cards/index rather than whole-world text.

## Math + Invariants Loop
- Per encounter option, run invariant checks with numeric before/after values.
- If any invariant fails, apply minimal correction and record it in phase logs.
- Keep corrections deterministic so benchmark diffs remain attributable to model condition.

## MCP Tools
- `list_encounters`
- `get_context_card`
- `get_mathematical_poetics_card`
- `get_iteration_packet`
- `update_encounter_block`
- `export_encounter_index`

## Benchmark Discipline
- Keep decoding parameters fixed across model conditions.
- Keep encounter order fixed.
- Keep max encounters/pass count fixed.
- Log per-encounter latency, parse success, and ID-preservation.
- Split parse metrics into:
  - raw model formatting (`model_parse_ok`),
  - repaired pipeline formatting (`parse_ok`).
- Keep packet budgets fixed (`8192/1024/900`) so token economics are comparable across runs.

## Prompt Spec
- Use `references/MCP_ASSEMBLY_PIPELINE.md` as the default codex contract for phased MCP generation:
  - spool/encounter assembly in bounded chunks,
  - invariant math review,
  - act completion,
  - chunk-aware holistic appraisal.

## Repair Addendum: Ad Hoc Teacher Output → SweepWeave (2026-11-27)
Found while repairing `InkyWorlds/camelots-reckoning` (300 Inkling-2-Mini encounters generated by a
one-off `run_campaign.py` harness outside this skill, in a bespoke JSONL shape). Two separate gaps,
both silent until checked:

**1. Canonical checkout path.** Every script path in this repo's skills (`small-storyworld-builder`,
`storyworld-building`, `storyworld-conveyor`, and others) is hardcoded to `C:/projects/GPTStoryworld`
(or its WSL mirror `/mnt/c/projects/GPTStoryworld`). That path did not exist; four other linked
worktrees of this same repo were scattered across `Documents/Codex`, `Documents/GitHub/MoralityLabAI`
and `D:/Codex-offload`, none at the path the skills assume. Consolidated to one worktree at
`C:/projects/GPTStoryworld` (`git worktree add /c/projects/GPTStoryworld origin/main --detach`,
sharing the same `.git` as the other worktrees of this repo) so the hardcoded commands in this file
and the others actually resolve. Before running any skill command from a fresh clone or agent
session, confirm `C:/projects/GPTStoryworld` exists and is this repo, or every path in this file is
silently wrong.

**2. Schema repair before claiming SweepWeave-compatible.** `sweepweave_validator.py` is the ground
truth for "is this a valid storyworld," not `storyworld_format_guide.md`'s simplified example — the
guide's sample spool omits two fields the real validator requires:
- every spool needs an explicit `"encounters": [id, ...]` list (membership is NOT inferred from
  encounters' own `connected_spools`, despite that field existing on the encounter side too);
- at least one spool needs `"starts_active": true`, or validation fails with `no starts_active spool`.

Checklist for repairing any ad hoc encounter set (JSONL, bespoke JSON, etc.) into this schema:
1. Build `characters` (`id`/`name`) and leave `authored_properties: []` if the source content has no
   simulated state — don't invent BNumber axes the generation never produced.
2. One spool per narrative grouping (acts, branches, endings), each carrying its own `encounters` id
   list in play order, and `starts_active` set correctly for the true entry point(s).
3. One page per encounter: `text_script` copied verbatim (never rewritten), `options` → one or more
   `reactions`, each reaction's `consequence_id` pointing at a real encounter id (or the literal
   string `"wild"`, the validator's one exception). A true terminal node is `"options": []`, not an
   option with no reactions.
4. A branch point with more outcomes than the source gave discrete options for (e.g. "this could tip
   toward any of 11 endings") is modeled as one option whose `reactions` array lists all of the
   possible `consequence_id`s with equal `desirability_script` weight — not forced into a 1:1
   option-to-branch mapping that doesn't exist in the source.
5. Run `sweepweave_validator.py validate <out.json>` immediately. `VALID OK` or it isn't done.
6. Then run `storyworld_quality_gate.py --strict` and actually read the per-check breakdown, not just
   `pass`/`fail`. A single-pass teacher-generation output with no BNumbers, no conditional
   `visibility_script`/`performability_script`, and constant `desirability_script` everywhere will
   validate cleanly and still fail the quality gate hard (Camelot's Reckoning: 6/28 checks passed,
   `overall pass: false` — every mechanics-richness check failed, both narrative-quality checks
   passed). Schema-valid and quality-gate-passing are different bars; don't report one as the other.
   Closing that second gap needs an artistry/effects pass (`apply_artistry_pass.py`,
   `add_effects.py`, `systematic_desirability_rewrite.py`) over the repaired JSON, which this
   addendum does not attempt — it only gets a storyworld to `VALID OK`.

Reference implementation: `InkyWorlds/camelots-reckoning/to_storyworld_json.py` (Camelot-specific
topology — trunk, 11 branches, one 11-way fan-out point — but the checklist above is the general
form; copy the pattern, not the branch count).
