# The Hat That Held the Moon

A 20-scene illustrated village fable, written by Inky Mini (`inky-mini-varloop`,
`TML-d24-varloop-research-IQ4_NL.gguf`, 2 loops, 16,384-token context, Vulkan) through Goose and
Pocket Goblin (`goblin-gdk`). It was built with this repository's
`codex-skills/small-storyworld-builder` skill and validator at commit
`c8d46591f983473023daf0232e9b413baaa02194`. The driver, HybridTRMLDT
`MCP/mcp05/inky_storyworld.py`, asked for one stage per turn: world card, outline, encounters four at
a time, balance revisions, art and the player.

Shape: 20 scenes, 16 of them with choices, 48 choices, 96 reactions, 4 characters (Pip, Mara, Old Fen
and the Moon), and three village meters (Trust, Nerve, Care). There are 4 endings: `end_return`,
`end_keep`, `end_share` and `end_fallback`. A seeded 5,000-run rehearsal with uniform random choices
visited all 20 scenes and reached all 4 endings; `end_keep` is the rare one, at 33 of 5,000.

Play: open `index.html` in a browser for the original edition, or `picture-book/index.html` for the
picture-book edition. Both load only the scripts beside them.

## Files

- `storyworld.json`: the world in SweepWeave JSON.
- `world.swmd.min.md`: the same world in SWMD.
- `balance.json`: the rehearsal and balance data.
- `index.html`, `player.js`, `art.js`, `world-data.js`: the original edition's player.
- `manifest.json`: the export's hashes, the skill and validator versions, and the browser check.
- `picture-book/`: a later pass in which Inky restyled the page and the art (`index.html`, `art.js`).
  `player.js`, `world-data.js` and `balance.json` are unchanged.
- `receipts/`: the run receipt (`inky-storyworld-cat-hat-receipt.json`) and the picture-book receipt
  (`inky-storybook-style-receipt.json`).

## Verification

Both editions' browser checks are `verified`: 20 distinct Canvas scenes through the player controls,
response formulas and bounded effects that match an independent replay, and every ending plus restart
working. The hashes in `manifest.json` and `picture-book/manifest.json` match the files here, and the
two manifests' own hashes match the picture-book receipt.

## Provenance

Run `inky-cat-hat-20261123`, written 2026-11-23 to 2026-11-24. The receipts come from
MoralityLabAI/HybridTRMLDT, branch `research/mms-mcp-spatial-20261126`, commits `707b6b6` (the run) and
`6dec1e7` (the picture-book edition). The world files are that run's exports.
