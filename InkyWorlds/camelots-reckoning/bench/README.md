# Repair-pass bench: can Inky reproduce the schema repair itself?

`to_storyworld_json.py` (one directory up) converted Camelot's 300 raw encounters into the
standard SweepWeave schema by hand-written code. This bench asks whether Inkling-2-Mini can do
that same per-encounter repair step itself, given only the checklist now written into
`codex-skills/small-storyworld-builder/SKILL.md`'s Repair Addendum — not the ground-truth output.

## Method
`bench_repair.py` samples 8 encounters covering every structural case in the checklist: five
ordinary single-reaction encounters, two terminal endings (empty `options`), and the one 11-way
branch-point fan-out (the trunk's final page, where every option must list all 11 ending-head
`consequence_id`s). Each raw encounter is handed to Inky with the repair rules and nothing else;
its reply is scored against the known-good page already in `../storyworld.json` (itself `VALID OK`
under the repo's `sweepweave_validator.py`), and separately re-validated live by substituting its
page into a copy of that storyworld and running the real validator against it.

## Result (2026-11-27, Inkling-2-Mini via squid5080/goblin-gdk)
**8/8** on every axis: `parse_ok`, all per-type structural checks (id preserved, scene/option text
copied verbatim, option/reaction counts and `consequence_id` targets correct, terminal pages
correctly emptied of options, the 11-way fan-out correctly completed and per-option), and
`sweepweave_validator.py` `VALID OK` on the reconstructed mini-world.

One real finding en route: the 11-way fan-out case needed roughly 9000 output tokens (22-33
reaction objects in one JSON reply); at 4096 it was truncated mid-reply with otherwise-correct,
in-order output, not a reasoning failure. `bench_repair_results.json` is the raw per-item score
log from the passing run.
