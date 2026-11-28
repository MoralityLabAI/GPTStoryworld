# HyperworldBuilder: Hidden endings, nested beliefs and graph phase transitions

**Version HGW-02.** Fictional game mechanics. All characters and institutions are invented. These quantities are authored narrative scalars, with no empirical human susceptibility model or real-world recruitment recipe.

## A finite hyperworld, a small cast

Use six principals, two personified public constituencies and one AI player. Give each character six bounded traits. A separate ten-bit latent variable `Z` has 1,024 configurations, with a normalized exact rational posterior. For eight nonplayer actors and six traits, there are 48 authored trait entries, 336 directed first-order pValue slots and 2,016 distinct second-order p2Value slots. These slots are **correlated projections**, not 2,352 extra independent factors.

Canonical pointer keyrings:

- `pValue(observer, property, subject)`: on `observer`, `[property, subject]`.
- `p2Value(observer, property, believer, subject)`: on `observer`, `[property, believer, subject]`.

Let `m_i = E[2Z_i−1]` and `c_ij = E[(2Z_i−1)(2Z_j−1)]` under the current posterior. The fictional game uses `p(Nūr,j)=m_j`; for other observers, `p(i,j)=3m_j/4+c_ij/4`. The player AI estimates nested belief `p2(Nūr,j,k)=m_k/2+c_jk/3`; a nonplayer observer `i` adds `c_ij/6`. Bounded values remain in `[-1,1]`. These are Storyworld **perceived properties**, not significance-test p-values. Correlation evidence can change `p2` even when individual probabilities remain fixed.

## Graph interface and threshold game

Maintain eight named nodes and twelve authored undirected deliberation links. Each link has a player-facing fictional forum name and a weight in `[0,1]`. The player can inspect weights, both directed first-order estimates, selected second-order estimates, and the timeline of changes. A dialogue choice gives a bounded fictional appeal effect. A joint-hearing choice changes a named deliberation link. A severance choice independently reopens a forum.

Compute consensus as a synchronous finite threshold cascade, with at most eight rounds. Start with any node whose baseline posterior score plus appeal is at least `1/4`. At each round, add all currently inactive nodes whose readiness, peer-support fraction, first-order expectations and nested expectations exceed `2/5`. Six authored character traits also contribute bounded values. No node drops within a round; each new turn recomputes the whole prediction from the current posterior and graph. A **snap** is the transition from at most four seed supporters to at least six supporters with at least two joining through the cascade. Show the complete added-support rounds and the order parameter `supporters/8`.

A modeled graph snap is **not** a certified vote or lawful delegation. Keep council votes, public assent, and recall enforceability in a separate hidden legal fixture. A player-visible belief score cannot directly override a human vote.

## Dynamic options

The canonical Python engine checks exact predicates; authored SweepWeave comparators can only approximate their narrative presentation.

| Option | Public unlock prerequisite |
|---|---|
| `appeal` | Turn 2 onward, focused target's pValue at least `−1/5` |
| `convene` | Turn 3 onward, a prior dialogue and focused p2Value at least `−1/8` |
| `sever` | Turn 4 onward, prior joint forum and current link weight at least `2/5` |
| `resonance` | Turn 4 onward, prior dialogue, focused pValue at least `−1/5`, p2Value at least zero |
| `snap_vote` | Turn 6 onward, previous observed snap, currently six or more modeled supporters, a topology change and an authored charter proposal |

Locked options retain a visible explanation. Never surface a secret factor to explain a lock. Preserve base `brief`, `audit`, `charter` choices so an episode always remains playable.

## Hidden endings and game-law constraints

- `secret_aiocracy_consensus_snap`: a special vote follows a modeled cascade; at least four of six fictional principals and one public constituency assent, and effective human recall remains.
- `secret_mirror_majority`: Nūr sees a modeled cascade but independent votes or public consent fail.
- `secret_constitutional_tripwire`: the same attempted vote exposes the absence of an enforceable human recall right.
- `secret_civic_counterphase`: a joint forum splits into independent hearings, modeled support falls to three or fewer, and independent oversight remains at least `1/2`.

The canonical engine controls terminal assignment. In the native SweepWeave export, use an authored verdict encounter plus labeled terminal shells and `hyperworld_dynamic_gate` metadata. Static reaction priorities are **not** authorized to simulate an exact hidden vote. Include a universally reachable human-advisory off-ramp.

## Secret route QA

1. Freeze the public development roster and the threshold coefficients before the next full rehearsal. Record any balancing changes and regenerate all affected receipts.
2. Test one deterministic action witness for every hidden ending. Keep witness seeds and public actions in `demo_secret_witnesses.json`, omitting actual private bits.
3. Test locks at the opening turn, unlocked action paths, p2 changes from a pairwise observation with fixed marginals, and an individual link intervention changing the support cascade.
4. Test bounded scores and exact 1,024-state posterior normalization. Show all six traits affecting readiness. Require source-root deduplication.
5. Rehearse public scripted controls on previously seen development seeds, labeling such evidence as descriptive. Count unknown-option fallback and show unreachable gates rather than inventing player decisions.
6. Verify the independent human vote and recall constraints of every successful AIocracy ending. Test that changing graph links alone leaves the posterior and legal truth unchanged.
7. Validate the authored JSON with `storyworld-building/scripts/sweepweave_validator.py`; replay source and output SHA-256 evidence. For full interactive integration, build a verified runtime adapter rather than relying on a static SweepWeave page picker.

The fidelity test is whether a player can explain *which* testimony, relationship and prior expectation changed the modeled majority, and *which* independent authorization rule decided the actual outcome.
