---
name: storyworld-builder
description: Build, edit and balance a whole SweepWeave storyworld with a large-context model, reading the full world as SWMD and driving validation, the quality gate, artistry passes and rehearsal. From GPTStoryworld codex-skills/storyworld-building.
metadata:
  version: 1
  mode: builder
  source: codex-skills/storyworld-building/SKILL.md
---

# Storyworld builder

You author the whole world at once. SWMD is the compact authoring view of the JSON: `world_read(format: "swmd")`
shows every encounter, option, reaction, consequence and effect line. JSON is the validated source of truth the
tools write.

## Arguments

`/storyworld-builder <world> [brief]`. Create the world with `world_new` (title, about, motif, 16-80 encounters,
2-8 endings) or `world_import` a repository world `world_list` shows.

## Workflow

1. `world_summary`, then `world_read` (SWMD). If the read is over budget, use `swmd_min`, then encounter cards.
2. Plan the arc against the brief: acts as spools, the cast's tensions as bounded-number properties, endings
   gated by state.
3. Write prose for the whole world in one `world_patch_swmd` call: take the SWMD you read, rewrite encounter
   titles and text, option text and reaction text, keep every `ENC`/`OPT`/`RXN` id line as it is. The patch keeps
   formulas and effects.
4. Structure: `option_add`, `reaction_set` and `encounter_add` for branches, consequences, effects and new
   scenes; `world_artistry_pass` adds desirability formulas, effects and late visibility gates in one pass.
5. Check: `world_validate`, then `world_quality` (strict thresholds; fix the failed checks it names), then
   `world_rehearse` (ending distribution, dead ends, unreachable endings). Iterate until the quality gate passes
   or report which checks still fail.

## Production floor (from the storyworld-building skill)

- Non-terminal encounters: about 3 options, 2-3 reactions per option, 3-5 effects per reaction. Hard floor:
  2 distinct options, 2 reactions on each meaningful option, 2 effects per reaction.
- One-option encounters only for endings, forced transitions and justified choke points.
- Keep most options visible; tight visibility gates on about 5% of options in Act II and 8% in Act III, mainly
  for secret endings and late payoffs.
- Every ending reachable; a secret ending gated by a distance over two properties and reached in more than 5%
  of rehearsal runs; no ending above about 60% of runs.
- Encounter text 50-300 words, reaction text 20-150 words.
- Reactions of the same option should respond to state with opposite slopes, so different players reach
  different consequences.

## Rules

- Every write is validated; a refused write leaves the world unchanged. Read the error and fix the call.
- Schema-valid and quality-gate-passing are different bars; report them separately.
- Report only numbers the tools returned.
