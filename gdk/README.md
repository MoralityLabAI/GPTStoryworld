# Storyworld, a Goose GDK app

`storyworld` is a Rust app on the Goose GDK (`goose-agent` / `goose-providers` 0.1.0-alpha.14, the same pins as
Data Goblin and Pocket Goblin). It drives a local model through one of three skills taken from this repository's
own skills. A stdlib Python MCP server, `gdk/storyworld_mcp`, owns the worlds, the SweepWeave validator, the
quality gate, rehearsal and the hyperworld engine.

| skill | from | mode | context defaults | what the model can reach |
|---|---|---|---|---|
| `storyworld-builder` | `codex-skills/storyworld-building` | `builder` | 64K context, 8K output, 40K-token world reads | whole-world SWMD reads and patches, artistry pass, every encounter and structure tool |
| `small-storyworld` | `codex-skills/small-storyworld-builder` | `small` | 8K context, 1K output, 2.5K-token cards, newest 2 long tool results kept | one encounter card at a time and micro-edits; no whole-world read is listed |
| `hypergames` | `codex-skills/hyperworld-builder`, `verifiers_envs/storyworld-hypergames-env` | `hypergames` | 32K context, 4K output | exact-graded eval families from the Cairo hyperworld engine, held-out freeze, scoring |

The skill picks the server's tool mode, so the small model's request never lists a tool that pulls a whole world
into its window. In small mode the app also rewrites each request: tool results longer than 400 characters,
other than the newest two, become a one-line stub that says which tool to call again. The conversation and the
receipt keep the full results.

## Tools

Every write is checked with `sweepweave_validator.validate_storyworld`. A write that adds a validator error is
refused with the error and leaves the world unchanged. An edit that clears first-stage errors (missing top-level
keys), and so lets the validator reach errors it had not checked yet, counts as progress. Each world keeps
`.history/` snapshots and a `ledger.jsonl` of writes.

- Both authoring modes: `world_list`, `world_new` (`fresh_storyworld_seed.py`), `world_import` (a repository
  world, imported as it is so a broken world can be repaired), `world_summary`, `world_validate`,
  `world_quality` (`storyworld_quality_gate.evaluate_storyworld`, failed checks listed), `world_rehearse`
  (random play with wild routing, from `tools/probe_morality_batch_routing.run_episode`), `encounter_list`,
  `encounter_card`, `encounter_edit_text`, `option_add`, `reaction_set`, `encounter_add`, `world_set_fields`,
  `spool_set`, `character_add`.
- Builder only: `world_read` (SWMD, SWMD-min or JSON, up to the read budget), `world_export_swmd`,
  `world_patch_swmd` (`swmd_patch_json.patch_world`), `world_artistry_pass` (`apply_artistry_pass.apply_artistry`).
- Hypergames: `hyperworld_status`, `hyperworld_view`, `hyperworld_family_build`, `hyperworld_family_score`,
  `hyperworld_family_freeze`, `hg_selftest` (the hypergames env's unit tests and receipt checks).

`--approve read-only` hides and refuses every write. The app refuses a call identical to one that already
failed twice and names the error.

## Hypergame families

`hyperworld_family_build` plays the Cairo hyperworld (ten hidden binary factors, 1,024 worlds) from public dev
seeds and asks questions about the exact posterior, from the public evidence trace only:

- `marginal`: P(factor = 1).
- `parity`: P(a XOR b = 1).
- `p2_alignment`: the engine's second-order belief, 2 P(a = b) - 1, between two actors.
- `fresh_count`: how many evidence items carry independent information.

Each evidence item reports the parity of some factors through a binary symmetric channel. A relay of an earlier
source root carries no new information. The grader recomputes the posterior from the public trace with the
engine's own `update`, checks it equals the engine's posterior, and scores against three baselines: the oracle,
a naive baseline that counts every relay as fresh, and a uniform prior. A family is accepted only when the
oracle scores 1.0, the naive baseline scores at most 0.5 and the uniform baseline at most 0.25.
`hyperworld_family_freeze` draws held-out seeds into a directory outside the repository and records only their
SHA-256 in the manifest.

Measured on 16 dev seeds (0-15) at turns 4, 6 and 7, the defaults. `traps_only` keeps the items the naive
baseline gets wrong, and `max_items` (120) caps the runs where it is off:

| policy | traps_only | items | by kind | oracle | naive | uniform | accepted |
|---|---|---|---|---|---|---|---|
| `random` (seeded legal play, the default) | on | 54 | marginal 15, parity 12, p2_alignment 12, fresh_count 15 | 1.0 | 0.0 | 0.0 | yes |
| `random` | off | 120 | 30 of each kind | 1.0 | 0.833 | 0.367 | no |
| `mixed` | on | 96 | marginal 48, fresh_count 48 | 1.0 | 0.0 | 0.0 | yes |
| `mixed` | off | 120 | 30 of each kind | 1.0 | 0.5 | 0.167 | yes |
| `charter` | on / off | 96 / 120 | as `mixed` | 1.0 | 0.0 / 0.5 | 0.0 / 0.167 | yes |
| `snap`, `civic`, `review` | on | 0 | no relays in these traces | - | - | - | no |
| `snap`, `civic`, `review` | off | 120 | 30 of each kind | 1.0 | 1.0 | 0.25-0.8 | no |

Only `random` produces relay traps for the parity and p2_alignment kinds; the scripted policies relay only
single-factor dispatches.

## StoryworldBench through the app

`storyworld bench --track builder|small|hypergames` runs `benchmarks/storyworld_bench` tasks through the app.
Each task gets a fresh workspace, and its server refuses the task's `grading_only` paths (oracle worlds, the
repaired Camelot world, the HG solver modules). Builder tasks run the `storyworld-builder` skill on a workspace
world named `bench`, which the bench scorer grades. Small and hypergames tasks are answered directly with that
mode's tools available, and the final answer is scored. Results go to
`<work>/bench/<track>-<split>/{results.jsonl,summary.json}` with one receipt per task. The test split needs
`--confirm-one-shot`.

## Build and run

```powershell
cd gdk
cargo +stable-x86_64-pc-windows-msvc build --release
```

On this machine, put `CARGO_TARGET_DIR` outside OneDrive (for example the BitAgent desktop target, which already
has the goose dependencies compiled). Point the app at a local OpenAI-compatible server. It talks to loopback
servers only.

```powershell
storyworld run --root . --python python --skill small-storyworld --args "lighthouse build a 16-scene lighthouse mystery" --base-url http://127.0.0.1:18090/v1 --model inkling-2-mini
storyworld run --root . --skill storyworld-builder --args "cairo tighten act two" --base-url http://127.0.0.1:18104/v1 --model bonsai-27b
storyworld run --root . --skill hypergames --args "relay-traps-v1 late-game items" --tool-mode text
storyworld bench --root . --track hypergames --limit 5 --base-url http://127.0.0.1:18090/v1 --model inkling-2-mini
storyworld tools --root . --mode small
```

Each run prints one JSON receipt and appends it to `<work>/receipts.jsonl`. The work dir defaults to
`gdk/work`, which git ignores. A receipt holds every tool call and result, the worlds touched with their last
validator status and quality summary, the families built, the writes and refused calls, the token usage (including
the largest single request), and an OpenAI-style transcript.

## Tests

```powershell
$env:PYTHONPATH = "gdk"; python -m unittest discover -s gdk/tests -p "test_*.py" -v
cd gdk; cargo test
python -I gdk/ci_smoke.py gdk/target/release/storyworld.exe --python python
```

`ci_smoke.py` runs the binary against a scripted OpenAI-compatible endpoint in three runs:

- `/small-storyworld` with native tool calls. It exercises the slash command, mode filtering, two server
  refusals, the repeated-failure guard, a valid option add, and elision of older results.
- `/hypergames` with the text tool protocol. A family is built and accepted.
- One `bench --track builder` task. The grading-only path is refused, the input world is imported, and the bench
  scores the result.

CI runs all of these on Ubuntu, together with the StoryworldBench tests and selftest
(`.github/workflows/storyworld-gdk.yml`).
