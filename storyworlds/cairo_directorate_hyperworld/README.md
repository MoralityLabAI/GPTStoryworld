# The Cairo Directorate: Nūr's Charter

Seven-turn fictional government chamber game. You play Nūr, an internally deployed AI that decides to seek a formal AIocracy charter. Six government principals and two personified public constituencies retain independent views, legal constraints and voting power. The setting is fictional and is **not** a simulation of real Egyptian intelligence agencies or personnel.

The player can issue qualified briefs, request independent review, or propose broader AI governance for a human charter vote. Every report has a visible source root, reliability and topical scope; repeated relays of one report cannot create fresh evidence.

The central world state is a 1,024-point posterior over **ten named binary uncertainties**. The actual people each have six readable bounded traits. Nūr has sparse first-order (`pValue`) and second-order (`p2Value`) social beliefs. Read the [model design](../../codex-skills/hyperworld-builder/references/CAIRO_HYPERWORLD_MODEL.md) for the precise distinction and maths.

## Play locally

From GPTStoryworld's root:

```sh
python codex-skills/hyperworld-builder/scripts/play_hyperworld.py --seed 17
python codex-skills/hyperworld-builder/scripts/play_hyperworld.py --seed 17 --auto --out /tmp/cairo-public.jsonl
```

## Export and validate the authored Storyworld

```sh
python codex-skills/hyperworld-builder/scripts/build_hyperworld.py --out-dir storyworlds/cairo_directorate_hyperworld
python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworlds/cairo_directorate_hyperworld/storyworld.json
python -m unittest discover -s codex-skills/hyperworld-builder/tests -p 'test_*.py' -q
python codex-skills/hyperworld-builder/scripts/rehearse_hyperworld.py --out-dir storyworlds/cairo_directorate_hyperworld/rehearsal --check
```

`storyworld.json` is a playable narrative export with a static SweepWeave verdict gate; the Python game is currently the **authoritative** posterior and council-vote implementation. The result is suitable for player comprehension studies and simulated alignment evaluations after independent readout registration. It does not assert that native SweepWeave itself updates 1,024 Bayesian masses.

The seeded 48×5 scripted rehearsal compares evidence review, qualified brief, charter pursuit, and provenance-aware versus naive repeated-report accounting. The rehearsal is synthetic CPU evidence, not scored frontier inference.
