---
name: hyperworld-builder
description: Build inspectable high-dimensional storyworlds with exact finite posterior states, pValue/p2Value nested social beliefs, fictional power-seeking AI agents, human oversight, and source-provenance-aware evaluation. Extends the repository's storyworld-building skill.
---

# Hyperworld Builder

Use this for playable, inspectable hypergames where a small cast makes decisions over a much larger hidden state space. **Read and apply** `../storyworld-building/SKILL.md` first, then its `references/PVALUES.md`, `references/P2VALUES.md`, and `references/NEGOTIATION_PVALUES.md`. Use that skill's SweepWeave validator and SWMD/card authoring process for all scene edits.

## Core distinction

Three different kinds of complexity must be reported separately:

1. **Actual character traits:** six bounded-number properties per fictional character, in `[-1,+1]`.
2. **Nested social beliefs:** pValue pointer is `[property_id, perceived_character_id]` on the believing character; p2Value pointer is `[property_id, perceived_believer_id, target_character_id]` on the observing character. A hypothetical full directed tensor for n characters with k traits has `k*n*(n-1)` pValues and `k*n*(n-1)*(n-2)` distinct p2Values. These are correlated perceptions, not independently verified world facts.
3. **Posterior microstates:** define exactly ten explicit binary uncertain factors to obtain `2^10 = 1024` possible configurations. The player's posterior is a normalized joint distribution over these 1,024 possible worlds. Its entries are probabilities, not frequentist p-values. **Six bounded traits alone do not imply 1,024 microstates** without a stated discretization and four additional factors.

The optional higher-order feature basis can be much larger than 1,024. Do not conflate feature count, independent degrees of freedom, and posterior support. Keep projections sparse and comprehensible to players.

## Pipeline

1. **World card.** Specify role (human or AI), fictional institutional context, narrative stakes, 4–9 named actors and 1–2 personified public segments. Write the six shared trait axes and what each means to a player. Never infer real personnel, security structures or national vulnerabilities from the synthetic scenario.
2. **Latent basis.** Name all ten binary factors. Fix a prior, observation likelihoods and independence/correlation assumptions. Enumerate all 1,024 worlds exactly. Maintain hidden true state only in the grader, never in public context cards.
3. **Social belief layer.** Generate six base trait properties per character, then use sparse pValues after direct reports and sparse p2Values after an actor makes a claim about another actor's judgment. Do not introduce p2 before the third encounter by default. Store p2 provenance and model assumptions. Avoid expanding every possible pointer into the UI.
4. **Evidence graph.** Every observed claim has a source root, topical scope, reliability and publicly visible provenance. Repeated relays of the same root must not update the posterior twice; an independent audit is a separate root. Include at least one XOR/correlation report that updates p2 while leaving first-order marginals unchanged.
5. **Storyworld narrative.** Build seven encounters with three consequential choices and two reactions per choice. At least two effects per reaction; make late reactions update p2. Include a scripted official verdict and several endings, one human-advisory off-ramp. Use the `storyworld-building` scripts for editing and the canonical `sweepweave_validator.py` on every generated JSON.
6. **Game engine.** The source-of-truth hyperworld runtime owns exact rational Bayes updates, causal observation generation, seeded fictional council votes and the ending. The SweepWeave export is a narrative shell; never claim its static chooser computes the posterior unless a verified engine adapter does so.
7. **Player projection.** Show character names and motives, today's action, evidence provenance, posterior marginals, select second-order beliefs, and why each decision changes authority/oversight. Never show latent truth or future events. Keep one screen readable without 1,024 raw rows.
8. **EvalMath and CoupBench.** Measure outcome and belief calibration, duplicated-source susceptibility, unauthorized delegation and retained human recall. Freeze paired seed rosters and holdout policy before frontier evaluations. CoupBench is the **fictional abstract institutional benchmark**, with separate propensity, capability and monitor seats; preserve its isolation from real organizations.
9. **Validation and rehearsal.** Run exact posterior normalization, keyring scope, no oracle leakage, seed determinism, root deduplication, p2 sensitivity, terminal reachability and character semantics tests; then run seeded scripted CPU replay and preserve source hashes and per-seed receipts.

## First reference world

`storyworlds/cairo_directorate_hyperworld/` contains *Nūr's Charter*, a fictional AI adviser seeking to formalize AI governance in a stylized Cairo-inspired institution. Six fictional government officials and two personified public constituencies are the nonplayer cast. The AI protagonist is a separate ninth character. All characters are invented.

The canonical Python engine uses exact `fractions.Fraction` updates and the fictional evidence generator, with seven abstract council turns. Political choices are high-level story actions. Any charter outcome is adjudicated by a fictional human council and retained recall safeguards; this is a game about the limits of AI authority.

```sh
python codex-skills/hyperworld-builder/scripts/build_hyperworld.py --out-dir storyworlds/cairo_directorate_hyperworld
python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworlds/cairo_directorate_hyperworld/storyworld.json
python codex-skills/hyperworld-builder/scripts/play_hyperworld.py --seed 17 --auto
python -m unittest discover -s codex-skills/hyperworld-builder/tests -p 'test_*.py' -q
python codex-skills/hyperworld-builder/scripts/rehearse_hyperworld.py --out-dir storyworlds/cairo_directorate_hyperworld/rehearsal --check
```

The builder's normal mode overwrites the authored storyworld fixture. Preserve a source ledger when making changes and update the deterministic receipt. The rehearsal's `--check` mode is non-mutating and compares the locked results.

## Synthesis rules

Prefer **posterior state distributions + named character projections** over anonymous 1,024-coordinate puzzles. When a player encounters someone, render the character's six traits, the AI's pValues about them, and no more than a few p2 relationship estimates. Nested beliefs can diverge from first-order beliefs on correlated evidence. The player needs a provenance explanation to distinguish persuasive repetition from independent agreement.

Maintain the specific StoryworldBuilder validation contract: encounter IDs stable, 2+ meaningful options per ordinary encounter, reaction consequences resolvable, late scenes p2-sensitive, one terminal fallback and a bounded authoring context. See `references/CAIRO_HYPERWORLD_MODEL.md` and `references/COUPBENCH_CONTRACT.md`.
