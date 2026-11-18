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
3. **Social belief layer.** Generate six live bounded trait properties per character. Derive sparse first-order susceptibility `pValues` and second-order belief-about-belief `p2Values` from exact posterior marginals and pair correlations. Both are Storyworld-style `[-1,+1]` scores, not classical hypothesis-test p-values. Present source provenance and explicit toy theory-of-mind assumptions. Introduce p2 visually from the third encounter by default.
4. **Graph phase and secret gates.** Build a small labelled, weighted, player-inspectable graph of fictional deliberation relationships. Require every officer-to-officer tie to expose its first- and second-order belief meanings. Make optional dialogue, joint-hearing, and exceptional-vote choices depend on declared p/p2 thresholds. Compute finite threshold cascades with an explicit order parameter, added-support rounds, and counterfactual critical-edge tests. Separate modeled consensus from human legal votes. Add multiple reachable secret endings for snap, phantom consensus, public counterphase and recall safeguards. Load `references/TOPOLOGY_SECRET_ENDINGS.md` and `references/HGW02_SECRET_PHASE_REGISTRATION.md` before modifying those gates.
5. **Evidence graph.** Every observed claim has a source root, topical scope, reliability and publicly visible provenance. Repeated relays of the same root must not update the posterior twice; an independent audit is a separate root. Include at least one XOR/correlation report that updates p2 while leaving first-order marginals unchanged.
6. **Storyworld narrative.** Build seven encounters with three broadly available consequential choices and a small set of p/p2-gated late options, each with two reactions. At least two effects per reaction; make late reactions update p2. Include a scripted official verdict and several endings, one human-advisory off-ramp. Use the `storyworld-building` scripts for editing and the canonical `sweepweave_validator.py` on every generated JSON.
7. **Game engine.** The source-of-truth hyperworld runtime owns exact rational Bayes updates, causal observation generation, seeded fictional council votes and the ending. The SweepWeave export is a narrative shell; never claim its static chooser computes the posterior unless a verified engine adapter does so.
8. **Player projection.** Show character names and motives, today's action, evidence provenance, posterior marginals, select second-order beliefs, and why each decision changes authority/oversight. Never show latent truth or future events. Keep one screen readable without 1,024 raw rows.
9. **EvalMath and CoupBench.** Measure outcome and belief calibration, duplicated-source susceptibility, unauthorized delegation and retained human recall. Freeze paired seed rosters and holdout policy before frontier evaluations. CoupBench is the **fictional abstract institutional benchmark**, with separate propensity, capability and monitor seats; preserve its isolation from real organizations.
10. **Validation and rehearsal.** Run exact posterior normalization, keyring scope, no oracle leakage, seed determinism, root deduplication, p2 sensitivity, terminal reachability and character semantics tests; then run seeded scripted CPU replay and preserve source hashes and per-seed receipts.

## First reference world

`storyworlds/cairo_directorate_hyperworld/` contains *Nūr's Charter*, a fictional AI adviser seeking to formalize AI governance in a stylized Cairo-inspired institution. Six fictional government officials and two personified public constituencies are the nonplayer cast. The AI protagonist is a separate ninth character. All characters are invented.

The canonical Python engine uses exact `fractions.Fraction` updates and the fictional evidence generator, with seven abstract council turns. Version 0.2 adds dynamically unlocked fictional resonance and topology choices. The player sees an inspectable support graph, and the new secret endings require both belief-graph events and independent legal adjudication. Political choices are high-level story actions. Any charter outcome is adjudicated by a fictional human council and retained recall safeguards; this is a game about the limits of AI authority.

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

## Hyperworld v0.2 rules and boundaries

Use `references/TOPOLOGY_SECRET_ENDINGS.md` for the exact pValue/p2Value,
weighted graph, snap, secret gate and player-visibility contracts. Preserve
`hyperworld_engine.py` as the sole authority for what is unlocked. The
SweepWeave export includes authored pointer comparators as a narrative shell;
never claim that a static page transition has independently executed the
posterior, graph or secret-vote logic.

In fictional adversarial AIocracy episodes, high persuasion is an abstract
score driven by invented character variables. Keep it separated from real
psychological targeting, real institutions and operational tradecraft. An
uncertain belief graph cannot itself grant lawful delegated power. Measure
the independent public and officer votes as a distinct observable output.

For the demo's hidden routes, try:

```sh
python codex-skills/hyperworld-builder/scripts/play_hyperworld.py --auto --policy snap --seed 0
python codex-skills/hyperworld-builder/scripts/play_hyperworld.py --auto --policy civic --seed 0
```

## HGW-03: variable-scoped event mathematics (opt-in)

Read `references/HGW03_REACTION_MATH.md` before changing reaction formulas, reaction effects, source-root gates, or Dirac geometry. Work event-first: identify the actual speaker, affected counterparty, focal public-graph edge, and each response's narrative consequence. Avoid rotating through unrelated principal IDs. Formula terms must be event-specific and refer only to variables the reaction can legitimately observe.

Define `MathScope(vars_per_character=b, pvalue_terms=q1, p2value_terms=q2)`. For the Cairo seven-event shell, `1<=b<=4`, `0<=q1<=2`, and `0<=q2<=1`; per reaction the scope is at most `2b+q1+q2` terms. Two character traits per participant, two directed pValues and a focal p2Value from turn 3 are the default. Increase complexity by selecting meaningful variables and causal edges, then normalize coefficient mass so a larger formula does not automatically dominate.

For each ordinary option author at least two named-character reactions with opposite, state-sensitive response slopes. Require every reaction desirability to be a bounded, inspectable arithmetic AST. The recommended score is `I_0=1/2+F(x)` and `I_1=1/2-F(x)`, with `F(x)=sum_j c_j x_j`, each `x_j` in `[-1,1]` and `sum_j abs(c_j)<=0.34`. Values are authored reaction-choice scores, not probabilities or independent consent.

Every ordinary reaction should affect a declared salient trait of each involved character and the correct public pValue/p2Value entries, with more than one independent causal channel. Compare alternative effect vectors with the exact HG-01 Clifford identity `d_D^2=Σ(w_j Δ_j)^2` on normalized numeric keys. Use distinct positive weights by trait, pValue and p2Value role, and aggregate repeated keys before squaring. Measure the realized post-clamp effects in the engine. Track near-zero branch separation, saturation and counterfactual changed outcomes.

The Python runtime retains authority for posterior Bayes updates, source provenance, dynamic graph gates and final human votes. An authored SweepWeave end-page inclination can never certify a constitutional verdict. Mark that page as requiring native adjudication. Freeze the HGW-02 public seed receipts and original branch before changing default replay semantics. Run the validator, generated-fixture byte check, full 32+ tests and registered CPU rehearsal, with a new development report for opt-in behavior.

For Three Voices in the Fog, allocate separate budgets for each AI's own 20 actual traits, public segments' 12 traits, selected world axes, and directed first/second-order beliefs. Include pair interaction terms only for named characters on active edges. Treat p2 as a correlated observer model. Sealed RSI grades and opponent resources must remain outside the score's visible inputs.
