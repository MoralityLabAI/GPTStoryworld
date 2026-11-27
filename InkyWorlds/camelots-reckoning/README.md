# Camelot's Reckoning

A 300-encounter Arthurian storyworld, written entirely by Inkling-2-Mini ("Inky Mini", served
locally via squid5080) through the goblin-gdk teacher-generation harness. No prose, options, or
scene text here was written by Claude; the orchestration code (`run_campaign.py`,
`build_outline_task.py`) only builds bounded prompts, validates and retries malformed replies, and
appends what the model returns. Each encounter also carries an Eyvind-Earle-style illustration
(`canvas_art_svg`) composed by the model for that exact scene.

Structure: a 51-encounter trunk at the Round Table, then 11 branches (22-23 encounters each)
toward 11 distinct named endings, round-robined so no branch gets ahead of the others.

## Files

- `outline.json` / `outline_ticket.json` / `outline_receipt.json` / `outline_task.txt` — the one
  planning call that produced the cast, setting, and the 11-ending branch outline.
- `encounters.jsonl` — all 300 encounter cards, one JSON object per line.
- `storyworld_bundle.json` — `{outline, encounters}`, what `viewer/index.html` fetches.
- `viewer/index.html` — the standalone reader (trunk playback, crossroads screen, branch/ending
  playback); open it from a local server so the `fetch()` of the sibling bundle works.
- `run_campaign.py` / `build_outline_task.py` — the orchestration scripts that drove the teacher
  calls and resumed across the shared GPU's power-cap interruptions.
- `state.json` / `campaign_run.log` — the final resumable-progress record and full run log.

## Provenance

Generated 2026-11-25/26 against `thinkingmachines/Inkling-2-Mini` (squid5080,
`C:\Users\patri\tools\squid5080`) through `goblin-gdk` in WSL. `evidence_class` on each encounter
is `"proposed"` — live-generated, not independently verified.
