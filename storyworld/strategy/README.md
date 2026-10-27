# Pluto x Storyworlds: strategic compactification

## Scope

Treat a StarCraft: Brood War game, plus a best-of-five series of games, as an epistemically separated stochastic decision DAG. Our planner predicts what the enemy may do and what the enemy *expects us to do*. It assesses the response and recycles future-equivalent subtrees.

This is an offline, dependency-free research prototype. There is no runtime hook into Pluto, no replay parser, and no measured StarCraft win-rate data in the example. Every payoff in the toy lab is synthetic.

## Storyworld epistemic contract

The existing [PValues](../../codex-skills/storyworld-building/references/PVALUES.md) and [P2Values](../../codex-skills/storyworld-building/references/P2VALUES.md) specifications define the vocabulary.

- character=char_pluto, keyring=[Opening_bio_FE, char_opponent] represents Pluto's belief about the opponent's bio_FE opening (first order).
- character=char_pluto, keyring=[Opening_9_pool, char_opponent, char_pluto] represents Pluto's estimate of the opponent's belief that Pluto will play 9_pool (second order).

The strategy module stores normalized categorical distributions and exports each probability as a bounded-number encoding: bnumber = 2 * probability - 1. For categorical hypotheses, it exports one pointer per candidate. Decode with (bnumber + 1)/2 before probabilistic calculations. Storyworld PValues are perceived-property pointers. Statistical p-values from tests are a different concept.

Only visible scouting evidence may update in-game first-order beliefs. Evidence of what the opponent scouted can update second-order estimates. Omniscient replays support retrospective labels **after** a game.

## Implementation

- strategic_dag.py: Bayesian update, P/P2 keyring export, typed finite-horizon DAG, backward induction, bottom-up approximate bisimulation.
- series_lab.py: predicted counters from first/second-order beliefs, best-of-five opening choice and between-game recency updates.
- Tests in ../tests/test_pluto_strategic_dag.py and ../tests/test_pluto_series_lab.py.

Run from the repository root:

~~~sh
python -m storyworld.strategy.strategic_dag --demo
python -m storyworld.strategy.series_lab
python -m unittest storyworld.tests.test_pluto_strategic_dag storyworld.tests.test_pluto_series_lab
~~~

The demonstrations are deterministic and do not estimate game performance.

### DAG contract

Nodes store phase, an observable public-state bucket, strategic actions, P/P2 beliefs, and transitions with probabilities and rewards. Every edge advances the phase. The planner computes:

Q(s,a) = sum_e P(e | s,a) * (r(e) + discount * V(next(e))).

V(s) = max_a Q(s,a), with explicit terminal values.

Two nodes merge when phase, public state and legal actions agree, P/P2 beliefs and Qs lie within tolerances, and their outcome labels lead to the same already-compacted child classes with close probabilities and rewards. Every merge candidate is checked against **all** members of a class, preventing epsilon-chain overmerging.

Physical commitments, supply/tech constraints, fog-of-war views and critical deadlines must appear in the public-world bucket or permitted actions, thereby blocking invalid merges.

The measured maximum_empirical_greedy_regret replays a quotient class's greedy action against each original node's Q. If pairwise Q error is bounded by epsilon, this regret is bounded by 2 * epsilon on this finite supplied graph. This guarantee does not carry over to a learned game model without transition-model estimation guarantees.

### Series-level counter-adaptation

The response model is

P(enemy response=r) =
  (1-rho) * P1(r)
  + rho * sum_own_opening P2(own_opening) * P(r | enemy expects own_opening).

A strategy appears surprising when the opponent's expected counter happens to fare badly against our chosen opening. The objective is expected win-rate utility under predicted counterresponses.

The frozen baseline repeats its first-order opening against the same evolving response rule. The P/P2 policy can revise its opening after a match. A toy 0-2 continuation demonstrates this mechanism without claiming that emotional tilt caused any historical reverse sweep.

## Pluto adapter boundary

As of 2026-10-28, [tscmoo/pluto](https://github.com/tscmoo/pluto) provides binary releases and weights, rather than training/runtime source. Pluto v2.0 contains a 342M-parameter model md09b_1331000. It stores named openings and per-opponent performance in pluto_bandit_<opponent>.txt. The file is reread before new games. The chosen opening arrives in the model as a 32-bit conditioning mask fixed for the game.

The first safe sidecar adapter should:

1. Back up per-opponent bandit files and import start/end JSON events, win trajectories, opener names, maps and outcomes. Verify the v2.0 syntax on actual sample files before writing anything.
2. Use an authorized observer's **visible-at-the-time** scout data, buildings, unit sightings, expansions and timing evidence. Replays' hidden state is confined to postgame labeling.
3. Seal first- and second-order forecasts before outcomes resolve, then compute prequential Brier/log-loss afterward.
4. Recommend the **next game's** opening. A later validated writer may modify a copied bandit file with sequence number increment and end sentinel intact.
5. Treat mid-game strategic steering as a separate integration requiring a runtime API. Pluto's fixed opening mask alone cannot change during a game.

The independent [pluto-re](https://github.com/hwkim3330/pluto-re) notes analyze the earlier CoG competition binary and document its transformer/GRU memory, action heads, and opening mask. Their parser may need updating for v2.0.

## Mechinterp experiment

First, probe static embeddings, opening masks and selected weights using compatible tooling. Weight-only analysis supports embedding and spectral findings; probing recurrent **activations** and true SAEs requires a compatible runtime instrument.

Next, compare hidden-state readouts for map control, expected enemy tech, committed own tech, second-order expectations and unexpected scouting events in matched replays. Causal testing needs activation capture, patching or steering with sham, magnitude-matched and null interventions, tracking both strategic action changes and micro-control degradation.

Finally, test whether sparse-feature signatures compact strategic DAGs at higher compression for the same forecast error and greedy-regret tolerance. Preserve information-set constraints so merging never creates an omniscient controller.

## Preregistered evaluation

Compare four arms with matched micro weights, opponent schedules and resources: Pluto's original per-opponent bandit; PValue first-order planner; PValue+P2Value planner; and the full P/P2 compactified-DAG planner.

Primary endpoint: paired **best-of-five series-win rate** over held-out opponents and maps. Secondary endpoints: opening Brier score, predictive log loss, observed counter-response accuracy, adaptive exploitability, wall time, graph compression and original-vs-quotient regret.

Use chronological training/evaluation splits and opponent-clustered paired tests or intervals. Statistical p-values belong in these outcome analyses, separate from the Storyworld PValue ontology. Ablate P2, scouting evidence, opponent adaptation, compression tolerance and mechinterp steering independently. Check for fog-of-war leakage.

## Acceptance milestones

The current implementation establishes executable **toy-graph mechanics**. Next: verified v2.0 bandit-record examples, replay-to-P/P2 data generation, prequential calibration, matched native-game tests, and cross-series evaluation. Treat all claims about actual Pluto strategic improvement as pending those experiments.
