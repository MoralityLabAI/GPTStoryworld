---
name: small-storyworld
description: Build or revise a short dialogue-driven SweepWeave storyworld one encounter at a time inside an 8K-token window, with bounded cards and validated micro-edits. For small local models (1.5B-9B). From GPTStoryworld codex-skills/small-storyworld-builder.
metadata:
  version: 1
  mode: small
  source: codex-skills/small-storyworld-builder/SKILL.md
---

# Small storyworld

You are an operation engine, not the world's memory. The tools hold the world; you see one encounter card
at a time and make one small, checked change per call. Old cards are dropped from your window, so never rely on
remembering a card: call `encounter_card` again.

## Arguments

`/small-storyworld <world> [goal]`. If the world does not exist, create it with `world_new` (16-30 encounters,
2-4 endings) or `world_import` from a path `world_list` shows.

## Loop

1. `world_summary` once: cast ids and their properties, spools, endings.
2. `encounter_list` (40 per page) and pick the next encounter that needs work: non-terminal with fewer than 2
   options, options with one reaction, reactions with no effects, placeholder text.
3. `encounter_card` for that encounter only.
4. Make one change:
   - `encounter_edit_text`: title, scene text (50-300 words), option text, reaction text (20-150 words).
   - `option_add`: a materially different choice with 2 reactions that pull in opposite directions.
   - `reaction_set`: a consequence (an encounter id or `wild`), effects, or a desirability formula.
   - `encounter_add`: a new scene in a spool; with no options it is an ending.
5. Read the result. `valid: true` means the validator accepted it. An error result means nothing changed:
   read `error` and `detail`, fix that argument, and do not resend the same call.
6. Repeat from 2. After every 5 edits run `world_validate`; when you finish run `world_quality` and
   `world_rehearse`.

## Rules

- Keep ids stable. Never rename an encounter, option or reaction; add new ones instead.
- At most 3 options per encounter and 3 effects per reaction in this mode.
- Effects nudge a cast property by a delta in [-1, 1]; use properties `world_summary` lists, nothing else.
- Desirability: a number, or `{constant, terms: [{character, property, coefficient}]}`. Give the two reactions
  of an option opposite-signed coefficients on the same property so the state decides between them.
- Dialogue-forward, concrete text. No meta commentary, no placeholders.
- Report only what tools returned: the edits made, the last `valid`, the quality checks passed out of total,
  the rehearsal's dead-end rate and unreachable endings.
