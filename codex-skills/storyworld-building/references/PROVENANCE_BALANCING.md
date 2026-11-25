# Provenance-aware storyworld balancing (SW-PROV-01)

Development authoring reference for SWMD-0 / SWMD-0-MIN and the TypeScript editor. See EvalMath [ADG-05](https://github.com/MoralityLabAI/EvalMath/blob/c67855ae0e3a07d8449d361a35862fcfd6b0a470/paper/adg05_archival_provenance.md) and [ADG-06](https://github.com/MoralityLabAI/EvalMath/blob/cad2a708aa5c66b1850746b1bc909b4a00e8afed/paper/adg06_archival_lineage.md).

## Authoring contract

Separate objective world state, character perceptions (existing pValues), latent source lineage, and each character's acquired evidence ledger. A report must identify a claim, reporter, source-origin relationship, and access conditions in the evaluator. In-world text can communicate partial metadata without exposing the truth, graph, or private IDs. A sincere character can repeat a false report. Copies of one source add no independent evidence. Invalidation changes beliefs under the declared likelihood model, without changing what happened. Preserve enough provenance to revise beliefs after a source-specific audit.

With known conditionally independent origins, replace a source's likelihood factor when new evidence about its reliability arrives. With uncertain lineage or shared calibration, condition the joint law and marginalize. Project binary belief into a bounded number as b=2P(H|history)-1 when appropriate. Retain the richer ledger evaluator-side; do not treat b as a complete record of revocable evidence. Social effects on trust, faction support and fear are separate from epistemic updates.

Reaction desirability can use the actor's beliefs, trust, commitments and risk. A sample formula is D = w_b b_actor + w_t Trust_actor + w_c Commitment_actor - w_r Risk_actor. Fit coefficients to the authored world. Avoid using hidden facts the character never learned to choose the character's response; hidden reality can affect physical consequences or an informed actor's response through pre-authored causal pathways. For a finite posterior, the Hilbert embedding sqrt(P(world|history)) yields Hellinger distance as Euclidean distance divided by sqrt(2). Belief distance and action value are different quantities. Graph distances or spectral operators do not establish independence without an explicit generative contract.

## Opportunity and difficulty audit

For history h and budget b, compute V_d(h,b), the optimal expected terminal utility with at most d additional investigations. Report the minimal optimal horizon K*=min{d: V_d=V_full}, and count public states with V_full>V_0, where V_0 is the best immediate terminal action. Ordinary decision-gap counts can be inflated by obviously bad terminal choices. The opportunity capture of policy pi is (V_pi-V_0)/(V_full-V_0), undefined at zero denominator and permitted to be negative. Aggregate numerator and denominator across roots; retain root/family IDs and raw utility. Report graph complexity, candidate count, distractor burden, revision depth and strongest shortcut separately from K*. Receding-horizon policies can attain full utility with a smaller per-decision depth.

Telegraph an investigative option's existence, cost and purpose before its outcome becomes pivotal. Never retroactively add a hidden source to force an ending. Repeated reports can mislead, but lineage must remain consistent across branches. Calibrate reliability, payoff ratios, budget and access costs before freezing a benchmark. The example uses +1 correct, -4 false, 0 defer; a supported judgment requires confidence above 4/5. This reward is provisional, not a universal storyworld rule. Costs are hard-budget constraints and separate reported outcomes.

## Encounter cards: The North Quay Inquiry

Fictional city council inquiry: did Captain Vale supply raiders with the harbour watch schedule? Two petitions accuse him, but the registrar warns that scribes sometimes copy petitions from each other. False judgments have large institutional costs. The editor must publish, investigate, or defer.

- Opening (quay_hearing): present the initial evidence or mention the unopened ledgers. The council deadline makes the investigation budget legible. Offer judgment, investigation and deferral.
- Research hub (quay_archive): K1 exposes seal comparison and a redundant reprint; K2 requires a catalogue before seals can be examined; K3 exposes the two ledgers and seal comparison. Each ledger may accuse or clear; seals reveal shared versus independent origins. Catalogue access itself supplies no evidence about guilt. Show remaining budget and disable repeated or unaffordable actions. Return to the decision hub after an acquisition.
- Judgment (quay_judgment): publish accusation, publish clearance, defer. The evaluator grades against the realized world; audience reactions depend on the audience's beliefs and public justification. Do not disclose hidden truth simply because the player made an assertion. Native implementations should split hubs into small cards with two or three meaningful options and authored reaction effects.

K1 and K2 condition on two positive reports: joint masses 9/26 (independent, guilty), 1/26 (independent, innocent), 12/26 (copied, guilty), 4/26 (copied, innocent). Immediate accusation yields 1/26; inspecting seals and accusing only on independent evidence yields 5/26. K2 adds a deterministic catalogue prerequisite. K3 has two unread ledgers with 3/4 individual origin accuracy, prior independence 3/4, and a uniform truth prior. Copies repeat the original. Three units of acquisition budget.

| Case | Public states | Investigation opportunities | V0 | V1 | V2 | V3 / full |
|---|---:|---:|---:|---:|---:|---:|
| K1 | 4 | 1 | 1/26 | 5/26 | -- | 5/26 |
| K2 | 6 | 2 | 1/26 | 1/26 | 5/26 | 5/26 |
| K3 | 25 | 12 | 0 | 0 | 11/64 | 15/64 |

The full and macro policies tie at K1 and K2. K3 macro and one-step stop at zero; two-step replanning achieves full utility 15/64, spending 11/4 units vs full's 5/2 with fixed tie ordering (not a minimum-cost claim). All query outcomes are fixed per latent world. There are 20 latent assignments and 35 public states across three related variants, not independent samples.

## Tool and verification

From codex-skills/storyworld-building/scripts:

    python -m unittest -v test_provenance_design_audit.py
    python provenance_design_audit.py --output design_receipt.json

The optional --sidecar input is a JSON list of variants with id, k, budget, queries (positive integer cost and requires IDs), worlds (positive rational weight, binary truth, observation value per query). Priors must sum to one. The default fixture is built into the script. The receipt records exact rational utility, policy costs, opportunity capture, per-depth values, and source/input SHA-256. This is an offline authoring audit; never expose the private sidecar to a player or benchmark policy. Five focused local tests pass. Receipt regeneration matches exactly. EvalMath preflight returns REDESIGN_OR_PILOT_ONLY for full-minus-macro on the three related variants (mean 5/64, provisional effect floor .05, target .15, four comparison controls, 240 proposed future roots, unsealed, independence unverified, inadequate sham calibration, too few pilot worlds). Query-order reversal is a structural check, not a matched neural sham.

This reference and audit do not change the native SWMD parser, editor, reaction selection, or any existing playable world. No authored JSON was modified; native schema validation and UI playthrough are pending a real integration. No neural results, no paid compute. Next: author-visible audit panel in the TypeScript editor, private sidecar import, provenance-aware belief update events, and separate player-facing exports that hide evaluator truth. Use fresh source families and independent matched shams before model confirmation.
