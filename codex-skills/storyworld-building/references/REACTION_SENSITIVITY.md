# SW-PROV-04: Reaction formula sensitivity and reachable endings

An offline exact authoring audit for a declared subset of SWMD-0-MIN, using the existing ENC/ORX syntax and a private JSON sidecar. See SW-PROV-03 for the evidence law. This is one finite design regression, not a trained-agent evaluation or proof of native-engine parity.

## Authoring checks

For a legal state x and available player option o, evaluate each reaction's desirability D_r(x), choose the first maximizing reaction in the listed order, and explore its explicitly linked consequence. For each coordinate j used in a score, perturb it to declared values while holding the other coordinates fixed. Report the number of changed winners, changed score vectors, and maximum absolute score shift. A zero observed flip rate means decision-inert on the tested probes; no probes means untested. Counterfactual coordinates may be off the reachable manifold. Score shifts alone do not establish decision relevance, and one-coordinate probes may miss interactions.

For reactions of the same option, compare destination plus complete post-effect state over reachable support. Mechanical equivalence does not imply equivalent dialogue, which minified SWMD may omit. A never-selected reaction is a candidate for author review rather than an automatic deletion. Report ties explicitly. For each selected effect, report raw and clamped changes, clipping, zero change and changes above a declared author-specific threshold. Explore every legal player option through the finite horizon. Ending status includes incoming attempts, guard-blocked states and a shortest witnessed action path. Unreached within the horizon does not establish general impossibility. Counts are unique encounter/turn/state tuples, not probabilities or independent worlds.

The interpreter is deliberately narrow: C/P and ADD/SUB/MUL/DIV/MIN/MAX, rational or decimal constants, SET and +=, explicit consequence IDs, listed-order effects clamped individually to [-1,1], unclamped reaction scores and first-winner ties. Initial states, conjunctions of simple numeric guards, perturbation values, entry, horizon and max_effect come from the sidecar. Frontmatter is not an executable guard source here. Spool scheduling, native acceptance scripts, other operators, hidden state, stochastic reactions, native export and TypeScript editor integration are outside scope. Reject unsupported records and missing links instead of silently approximating. A state-cap exception invalidates the complete audit.

## Council regression

From the SW-PROV-03 law derive 26 factual briefing ledgers with inspected provenance and/or validity. For each, project culpability b=2P(H|L)-1 and pair trust values 0 and 1/4; this gives 52 initial rows and 18 distinct projections. The two authored variants share this support. Both reproduce the original factual recommendation on every one of the 52 rows.

The deliberately flawed fixture has trust/8 in the accuse and clear formulas, a mechanically duplicate defer reaction, unconditional archive grant with raw delta +2 from zero and a gate Access >= 5/4 outside the bounded domain. Trust shifts scores by at most 1/32; it flips none of 18 paired probes. The 18 grant effects clip to +1 and exceed the provisional 1/4 threshold. The archive ending has 18 attempted entries and all are blocked. Two reactions are never selected, including archive refusal.

In the calibrated fixture remove the trust term from factual judgment and assign D(grant)=Trust-1/8, D(refuse)=0. Access increases by 1/4 on grant; the archive gate is Access >= 1/4. Nine reachable initial projections grant and nine refuse. Trust flips 18/18 paired archive probes; all nine grant transitions reach the archive ending with no clipped or excessive effects. Every reaction and ending is selected/reached on the declared support. One-coordinate culpability probes flip 60/80 verdicts in both variants. This is a designed social-access mechanism, not evidence that arbitrary trust thresholds or the new social policy improve realized narrative utility. The calibrated example terminates at archive access; subsequent discovery consequences still need authoring.

## Reproduction

From codex-skills/storyworld-building/scripts:

    python -m unittest -q test_reaction_sensitivity.py test_provenance_design_audit.py test_provenance_session.py test_provenance_characters.py
    python verify_reaction_sensitivity.py --output /tmp/reaction_receipt.json
    python verify_reaction_sensitivity.py --compact --output /tmp/reaction_receipt_compact.json

24 focused tests pass (eight new), ten receipt checks pass, both receipts regenerate byte for byte locally. The committed compact receipt hashes the complete exact result, including the generated private sidecars; the full downloadable bundle has those sidecars. Extract sidecars from the full receipt to audit either fixture independently:

    python reaction_sensitivity_audit.py north_quay_reaction_calibrated.swmd.min.md private_sidecar.json --output audit.json

One paired authored family, not independent samples; the 18 probes are not 18 independent units. The illustrative EvalMath preflight is REDESIGN_OR_PILOT_ONLY with one family, no independent sham calibration, no sealed holdout, provisional effect floor .05, target .15 and four planning comparisons. Reaction-order reversal of the calibrated archive decision leaves the flip statistic unchanged (structural sham only). This is a finite regression across different designed decisions, not a causal neural contrast. No model training or paid compute. Full repository CI and native editor validation remain unverified. Next: add live editor integration and audit a genuinely multi-hop storyworld in which access changes subsequent choices, beliefs and utility.
