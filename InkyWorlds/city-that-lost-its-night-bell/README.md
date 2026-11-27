# The City That Lost Its Night Bell

A 30-encounter storyworld with Canvas art, written by Inky Mini (`inky-mini-varloop`,
`TML-d24-varloop-research-IQ4_NL.gguf`, 2 loops, temperature 0, seed 523) through Goose and Pocket
Goblin (`goblin-gdk`) on an RTX 5080 Laptop GPU. The harness (HybridTRMLDT
`MCP/mcp05/hilbert_storyworld_bench.py` and `hilbert_canvas_bench.py`) split the authoring into
bounded stages: planning, characterization, the encounters, the endings, an art map, the page and the
Canvas renderer. It validated each turn and retried rejected ones. The accepted turn for every stage
is listed in `INKY_HILBERT_STORYWORLD_CANVAS_REPORT.md`; the largest accepted prompt was 3,401 tokens,
inside the 16K conveyor.

Shape: 30 encounters, 5,445 words of scene text, 90 options and 5 endings. Three endings are public
(`end_bell_returns`, `end_bell_sold`, `end_bell_lost_forever`). Two are secret (`end_bell_as_question`,
`end_bell_as_answer`), gated by a two-qubit state whose gates do not commute, so taking the same two
choices in the other order closes the gate.

Play: open `web/index.html` in a browser. It loads only the scripts beside it.

## Files

- `storyworld.hilbert.json`: plan, cast, scenes, endings, the Hilbert-space gating and balance data.
- `world.swmd.min.md`: the same world in SWMD.
- `sweepweave-topology.json`: the encounter graph in SweepWeave form.
- `web/`: the player (`index.html`, `player.js`, `art.js`, `world-data.js`).
- `screenshots/`: the start, act 3 and three endings, captured in headless Chrome.
- `INKY_HILBERT_STORYWORLD_CANVAS_REPORT.md`: per-stage turns, tokens and throughput.
- `receipts/`: the run receipt (`inky-hilbert-storyworld-canvas-receipt.json`), the browser receipt
  and the 16K/24K/32K planning receipts.

## Verification

The browser receipt is `verified`. It visited 32 scenes across encounters and endings, each with a
distinct Canvas render. The browser's two-qubit state and Born weights matched an exact reference
replay. Both secret endings were unlocked with exact Hilbert witnesses, and restart restored the
initial |00> state. The `export_sha256` hashes in the run
receipt match every file here. `receipts/browser-receipt.json` is kept with CRLF line endings
because its recorded hash was taken over those bytes; `.gitattributes` keeps the other text files at LF.

## Provenance

Copied from MoralityLabAI/HybridTRMLDT, branch `research/mms-mcp-spatial-20261126`, commit
`1307e7f9a38eb1afd63fb585b0cc80e297ddf1d9` (2026-11-24), `MCP/results/mcp05/inky-hilbert-16k/` and
the receipts beside it. That branch is open as HybridTRMLDT pull request 32.
