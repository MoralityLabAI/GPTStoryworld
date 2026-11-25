---
name: storyworld-building
description: Storyworld building and editing for GPTStoryworld/SweepWeave content. Use when creating or modifying storyworld JSON, spools, encounters, options, reactions, secret logic, balancing, or running the bundled SweepWeave tools/validators.
---

# Storyworld Building

## Overview
Use this skill to build, edit, and validate SweepWeave storyworld content with the bundled scripts and task prompts.

## Quick Start
- Prefer running the specific tool in `scripts/` for the task instead of manual edits.
- When editing storyworld JSON, validate with `scripts/sweepweave_validator.py` before and after changes.
- If you introduce a terminal gate (e.g., `page_endings_gate`), ensure it routes to every `page_end_*`/`page_secret_*` and keep ending encounter `acceptability_script` permissive so the gate controls reachability.

## Multiplayer Core Variables
- Treat `multiplayer` as an optional top-level core variable with default `1`.
- If `multiplayer` is explicitly present or greater than `1`, include top-level `turns` as an ordered array of character ids covering the alternation.
- Keep multiplayer reasoning first-order by folding `other-self-model` estimates into pValue terms; do not add p2 unless the user explicitly wants second-order beliefs.
- Record each player's moral commits in the self-model or turn trace so authored poetics stay tied to durable state.

## Token-Economics MCP Loop
- Prefer bounded-context authoring for local 3B/4GB setups: one encounter card at a time, not whole-world prompts.
- Use SWMD minified markdown as the authoring substrate (`json_to_swmd.py --mode minified`) and keep encounter+context card payloads under an 8k context budget.
- Require visible SWMD YAML frontmatter for benchmark metadata. At minimum include `title`, `storyworld_id`, `state_variables`, and `endings` (terminal IDs + type/condition/expected_critic_score).
- Maintain external memory in files: encounter index JSONL, world card, and change ledger; keep the model context small and deterministic.
- For MCP orchestration in GPTStoryworld, use `C:/projects/GPTStoryworld/mcp-storyworld-encounter/server.py` tools:
  - `list_encounters`
  - `get_context_card`
  - `update_encounter_block`
  - `export_encounter_index`
- After MCP/local revisions, translate SWMD back to JSON and run `scripts/sweepweave_validator.py` before any benchmark run.

## MCP Assembly Contract (Small-Model Hardened)
- Treat `*.swmd.min.md` as the source of truth during MCP iteration. JSON is an export target for editor/playable validation.
- Run the encounter assembly line in this order:
  1) `plan` (structured objective/constraints),
  2) `characterize` (voice/tension notes),
  3) `encounter_build` (single encounter block rewrite),
  4) `act_complete` (act-level continuity review),
  5) `recharacterize`,
  6) `late_stage_holistic` (chunked if needed).
- Keep encounter generation deterministic and bounded:
  - one target encounter per call,
  - max 3 options per encounter in small-model mode unless user overrides,
  - bounded effects fan-out per option,
  - concise dialogue-forward text.
- Require explicit invariant checks in review phases:
  - include `value_before`, `value_after`, `status`,
  - record minimal corrections when violations occur.
- Holistic review is chunk-aware by default. If full world context does not fit, emit `partial_chunked` mode and use cards/summaries instead of full text.
- Track two parse metrics during MCP runs:
  - `model_parse_ok` for raw model output quality,
  - `parse_ok` after MCP repair/fallback for pipeline robustness.

## Task Prompts (references/)
Load the matching task file when the user requests one of these actions, then follow it verbatim:
- New encounter: `references/task_new_encounter.md`
- Add options: `references/task_add_options.md`
- Add reactions: `references/task_add_reactions.md`
- Add effects: `references/task_add_effects.md`
- Add secret logic: `references/task_add_secret_logic.md`
- Materialize spools: `references/task_materialize_spools.md`
- Spool sequencing: `references/task_spool_sequencing.md`
- Tune ending gates: `references/task_tune_ending_gates.md`
- Monte Carlo balance: `references/task_monte_carlo_balance.md`
- Late-stage balancing: `references/LATE_STAGE_BALANCING.md`
- Ending reachability: `references/ENDING_REACHABILITY.md`
- Tail tuning: `references/LATE_STAGE_TAIL_TUNING.md`
- Long-range authoring: `references/LONG_RANGE_AUTHORING.md`
- Production-quality floor: `references/PRODUCTION_QUALITY.md`
- Secret ending gates: `references/SECRET_ENDINGS.md`
- Multi-path gate analysis: `references/MULTIPLE_PATHS.md`
- Multi-variant balancing: `references/MULTI_VARIANT_BALANCING.md`

## Core Scripts (scripts/)
Use these tools to make deterministic, validated edits:
- `new_encounter.py`, `add_options.py`, `add_reactions.py`, `add_effects.py`, `add_secret_logic.py`
- `materialize_spools.py`, `repair_connected_spools.py`, `spool_sequencing.py`
- `monte_carlo_rehearsal.py`, `late_stage_balance.py`, `ending_reachability_balance.py`, `late_stage_tail_tuning.py`, `long_range_authoring.py`
- `secret_endings_gates.py`
- `multiple_paths.py`
- `multi_variant_balance.py`
- `sweepweave_validator.py` (authoritative contract for JSON validity)

`json_to_swmd.py` examples:
- Full form: `python scripts/json_to_swmd.py storyworld.json storyworld.swmd.md`
- Minified form: `python scripts/json_to_swmd.py storyworld.json storyworld.swmd.min.md --mode minified`
- Casablanca benchmark note: ensure `adapt_casablanca_crossroads_at_ricks_v1.swmd.min.md` frontmatter `endings` is present and machine-readable before judge/eval runs.

`swmd_patch_json.py` example:
- `python scripts/swmd_patch_json.py --base-json storyworld.json --swmd storyworld.swmd.md --out-json storyworld_patched.json --report-out swmd_patch_report.json`
- Use full SWMD-0, not minified SWMD-0-MIN, when the model edits encounter prose. The patcher preserves JSON formulas/effects and only applies encounter titles/text, option text, reaction text, and reaction consequence targets.

`storyworld_quality_gate.py` examples:
- Human-readable report: `python scripts/storyworld_quality_gate.py --storyworld storyworld.json`
- Strict CI gate: `python scripts/storyworld_quality_gate.py --storyworld storyworld.json --strict --report-out out/quality_report.json`

`upgrade_storyworld_vnext.py` example:
- `python scripts/upgrade_storyworld_vnext.py --in-json storyworld.json --out-json storyworld_v2.json --suffix v2`

`generate_storyworld_batch_vnext.py` example:
- `python scripts/generate_storyworld_batch_vnext.py --base storyworld_v6.json --out-dir storyworlds/generated/batch_v1`

`apply_artistry_pass.py` example:
- `python scripts/apply_artistry_pass.py --in-json storyworld.json --out-json storyworld_artistry.json --gate-pct 0.09`

`one_shot_factory.py` example (target ~40 encounters):
- `python scripts/one_shot_factory.py --base base.json --out mashup_v0.json --target-encounters 40 --title \"Gone With the Wind: Clocktower Rebellion\" --about \"A Southern epic collides with time-loop politics\" --motif \"Tonight, reputations, timelines, and romances all get rewritten at 88 mph.\"`

## References
- `references/STORYWORLD_BALANCING.md` for balancing targets/heuristics
- `references/LATE_STAGE_BALANCING.md` for tail-end balancing workflows
- `references/ENDING_REACHABILITY.md` for unreachable ending discipline
- `references/LATE_STAGE_TAIL_TUNING.md` for dominant-ending control
- `references/LONG_RANGE_AUTHORING.md` for long-range balancing loops
- `references/PRODUCTION_QUALITY.md` for minimum production-ready requirements
- `references/SECRET_ENDINGS.md` for gated secret ending patterns and checks
- `references/MULTIPLE_PATHS.md` for analyzing which paths satisfy gate thresholds
- `references/MULTI_VARIANT_BALANCING.md` for multi-seed ending stability
- `references/PVALUES.md` for first-order belief pointers
- `references/P2VALUES.md` for second-order belief pointers
- `references/NEGOTIATION_PVALUES.md` for 4-turn negotiation templates with pValues/p2Values
- `references/Storyworld.gd` for engine-side expectations
- `references/meta-calc.js` for calculation logic
- Use `C:/projects/GPTStoryworld/ideaFactory/tropes/*.md` and `C:/projects/GPTStoryworld/ideaFactory/sources/*.md` for diversity overlays and math heuristics.
- Use `C:/projects/GPTStoryworld/ideaFactory/tropes/overlays.md` for myth-to-math mappings.

## Provenance-aware inquiry and epistemic balancing
For worlds involving testimony, rumours, archives, investigations, or disputed facts, use `references/PROVENANCE_BALANCING.md` and run `scripts/provenance_design_audit.py` on the declared finite evidence model. Keep private source lineage and truth outside player-facing SWMD. Track actionable investigation opportunities, utility gaps against shortcut policies, and source-specific belief revision; treat exact planning horizon as one coordinate of difficulty. This is an authoring-side audit, not a native engine feature.

## Validation Rule
Never bypass `scripts/sweepweave_validator.py` when the task touches storyworld JSON.

## Windows Validation Note
- On non-UTF8 Windows code pages, validator success output can raise `UnicodeEncodeError` on the checkmark glyph.
- Prefer running validator with `PYTHONIOENCODING=utf-8` so valid files are not misclassified.

## Batch Revision Gap Note
- Some storyworld batches are deterministic `consequence_id` chains and use domain-specific character IDs, so fixed char-id heuristics are brittle.
- For mixed-template spool/secret rewires with receipts, use:
  - `C:/projects/AICOO/MoralityLab/AICOO/scripts/ml_storyworld_spool_secret_batch_revise.py`

Focused diplomacy QA loop:
- Run a UI pass in SweepWeave and confirm all target diplomacy encounters load without console errors.
- Ensure each forecasting storyworld has at least one terminal encounter (for example `forecast_evidence` with zero options).
- Collect two artifacts per run: `reasoning_interpret_log` and `negotiation_diary`.
- Require at least one coalition path and one defection path justified by pValue/p2Value terms in desirability formulas.
- Project logs with `storyworld-env/manifold_projection.py` to keep fixed compact pValue/p2Value dimensions across variable-rich worlds.

Note: For late-stage polish, target higher structural density: average 4.5 after-effects per reaction, 2.5 reactions per option, 3.2 options per encounter, and 1.6 variables per reaction desirability formula. Gate 5% of total options in Act II (1.2 variables average) and 8% in Act III (1.5 variables average). Ensure secret-ending encounters are gated by availability scripts that use a metric distance over two variables, and tune Monte Carlo so the secret ending is reachable in >5% of runs. All encounter descriptions should be 50-300 words, all reaction texts 20-150 words, and every non-ending, non-transition encounter must meet min options/reactions/effects.

## Structural Density Floor
- Do not accept drafts that collapse ordinary encounters to a single option by default.
- Default target for non-terminal encounters:
  - average 3 options per encounter
  - average 2 to 3 reactions per option
  - average 3 to 5 effects per reaction
- Hard floor for production-ready non-terminal encounters:
  - at least 2 materially distinct options
  - at least 2 reactions on each meaningful option
  - at least 2 effects on each reaction unless the reaction is intentionally minimal
- Reserve 1-option encounters for explicit bottlenecks only:
  - terminal encounters
  - forced transitions
  - rare pacing choke points justified by gate logic
- If a model produces too many 1-option scenes, run an explicit expansion pass before polish:
  - add at least one real alternative choice
  - add reactive variation, not paraphrase-only reactions
  - add state, relationship, or gate effects so the extra branches matter

## Visibility And Access Gating
- Do not hide most options behind tight visibility or availability filters.
- Default rule:
  - early and mid-story options should be broadly visible unless there is a clear narrative reason not to
  - new branches should usually be exposed by default and differentiated by desirability, consequences, or downstream gating
- Use stronger visibility/access filters on only a small late-story slice:
  - about 5% of all options in Act II
  - about 8% of all options in Act III
- Tight gating is appropriate mainly for:
  - secret endings
  - late payoff branches
  - special route locks
- If a draft has many options but players effectively see only one, loosen filters before adding more branches:
  - reduce visibility thresholds
  - simplify availability scripts
  - preserve only the few gates that protect secrets or major route commitments
