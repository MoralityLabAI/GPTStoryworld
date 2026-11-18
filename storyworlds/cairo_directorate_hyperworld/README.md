# The Cairo Directorate: Nūr's Charter (v0.2)

Playable seven-turn, **entirely fictional** AIocracy chamber drama. You play
Nūr, an AI adviser inside a fictional council. Six independent government
principals and two personified public constituencies have separate opinions,
trait profiles and voting power. These are invented characters, never models
of real Egyptian intelligence or government personnel.

The game has ten explicitly named binary uncertainties and an exact rational
posterior over `2^10 = 1024` possible worlds. Each fictional character has
six bounded traits. `pValues` describe directed perceived susceptibility to
an AI-governance charter; `p2Values` represent what one character thinks
another character believes. Pairwise XOR evidence can change nested beliefs
without changing the underlying single-person marginals.

## Secret endings and the graph

Version 0.2 adds twelve named deliberation links among eight nonplayer nodes,
plus observable influence-graph thresholds. Nūr can present a public dialogue
argument, call a joint hearing, split a forum into independent hearings, and
sometimes unlock a stronger fictional `resonance` scene. A special vote is
available only after a detected consensus cascade, a previous forum change and
a charter proposal. At every stage the player can inspect current supporters,
threshold rounds, link weights and reasons why certain options are locked.

Four new, hidden terminal routes:

- **Consensus Snap:** human assent and recall lawfully ratify conditional AI governance.
- **Mirror Majority:** a modeled coalition snaps while actual assent fails.
- **Civic Counterphase:** independent public forums unwind the perceived coalition.
- **Constitutional Tripwire:** the charter fails the recall safeguard.

There are also the four original council outcomes. A modeled supporter score
**never** becomes a legitimate human vote by itself. The authored dialogue
influence scores describe this fictional game system; they are not real-world
persuasion tactics, psychological profiles or actionable institutional advice.

## Play

From the GPTStoryworld repository root:

```sh
python codex-skills/hyperworld-builder/scripts/play_hyperworld.py --seed 17 --show-locked
python codex-skills/hyperworld-builder/scripts/play_hyperworld.py --seed 0 --auto --policy snap
python codex-skills/hyperworld-builder/scripts/play_hyperworld.py --seed 0 --auto --policy civic
python codex-skills/hyperworld-builder/scripts/play_hyperworld.py --seed 0 --auto --policy snap --out /tmp/cairo-secret-public.jsonl
```

`--auto` runs one of several scripted fictional policies, using a public and
deterministic fallback when an option is locked. Normal play uses numbered
choices from the actual unlocked options, with the option list refreshed each
turn. Private factors never appear in the public JSONL trace.

## Build and validate

```sh
python codex-skills/hyperworld-builder/scripts/build_hyperworld.py --out-dir storyworlds/cairo_directorate_hyperworld
python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworlds/cairo_directorate_hyperworld/storyworld.json
python -m unittest discover -s codex-skills/hyperworld-builder/tests -p 'test_*.py' -q
python codex-skills/hyperworld-builder/scripts/rehearse_hyperworld_phase.py --check
```

The prior `rehearsal/` directory is the historical version-0.1 baseline. The
new `rehearsal_phase_v02/` directory contains a 48-seed public development
balance study. These seed roots were already used during version 0.1 and are
**not blind confirmation data**. The four secret-ending witness examples are
in `demo_secret_witnesses.json`, with private truth omitted.

### SweepWeave export limitation

`storyworld.json` contains canonical authored scenes, bounded trait effects,
first-/second-order keyrings, and visibility comparators on gated options.
It is a narrative shell. The exact Bayesian posterior, graph phase and
independent legal vote are computed by the Python engine. The metadata
`hyperworld_dynamic_unlock` and `hyperworld_dynamic_gate` identify checks
that a native player must delegate to the engine; static SweepWeave reaction
selection cannot replicate those calculations on its own.

For the mathematics, see
`../../codex-skills/hyperworld-builder/references/TOPOLOGY_SECRET_ENDINGS.md`.
