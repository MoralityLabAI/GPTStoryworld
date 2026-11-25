# SW-PROV-05: Social access as an instrumental epistemic mechanism

Development authoring reference. Extend SW-PROV-03's 24 positive-mass latent assignments with a conditionally independent noisy dispatch C, accuracy 2/3, yielding 48 assignments. The editor initially knows A; the registrar also initially knows A. Consult reveals B for one unit, seals reveal shared versus independent origin for one unit, and dispatch reveals C for two units. After seals, a one-unit briefing transfers all acquired evidence to the registrar and sets Trust to 1/4. Applying costs one unit; the registrar's score for granting is Trust - 1/8, and the score for refusal is zero (refuse on ties). A single application is allowed, as disclosed at the opening. A grant enables a further unit-cost registry read revealing A's validity. Truth and reports are fixed throughout the session. Reading the registry privately changes the editor's ledger only. Later briefing is not available in this fixture.

The social route has four acquisition steps. Each has a declared causal purpose. There is no terminal endorsement bonus: correct assertion pays +1, false assertion -4, and deferral 0. For known posterior p, assertion is profitable only when confidence exceeds 4/5. Acquisition costs are hard-budget constraints; utility ties favor stopping, then use a fixed action order rather than minimizing cost.

Controls retain the same latent law and terminal reward. Blocked removes briefing, application and registry; ungated removes briefing/application and makes registry directly accessible at its original one-unit read cost. The route heuristic prices the entire available archive sequence, including the stochastic seal observation, with terminal judgment at its end; it also prices immediate evidence queries, and replans after each step. Full planning recursively optimizes over all legal acquisitions, remaining budget and public belief state. One- and two-step policies truncate and replan. Costs are hypothetical authored units, not measured effort.

## Exact outcomes

| Budget | Blocked | Social | Ungated | One-step | Two-step | Route heuristic |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 3/8 | 3/8 | 49/72 | 3/8 | 3/8 | 3/8 |
| 3 | 11/24 | 11/24 | 25/36 | 41/108 | 11/24 | 41/108 |
| 4 | 11/24 | 2/3 | 17/24 | 11/24 | 11/24 | 2/3 |
| 5 | 11/24 | 25/36 | 13/18 | 11/24 | 5/8 | 25/36 |
| 6 | 11/24 | 25/36 | 13/18 | 11/24 | 5/8 | 25/36 |
| 7 | 11/24 | 13/18 | 13/18 | 11/24 | 5/8 | 13/18 |

At budget five, the social full policy gains 17/72 utility over blocked; the route heuristic ties full utility, spending 25/6 instead of 47/12 units on average. Mean full-minus-route utility over all six related budgets is 17/1296, below the provisional .05 effect floor. These are six budget settings of one authored law, not independent samples. The ungated comparison also changes access cost. No model training, neural mechanism claim or paid compute. The preflight remains REDESIGN_OR_PILOT_ONLY, with insufficient independent shams, no sealed holdout and insufficient meaningful headroom over the route control. The zero order-sham specification is a structural symmetry, checked with reverse enumeration of the budget-four packet-tree oracle, not neural sham calibration.

Witness: harbour A accuses and customs B clears; the seals establish independent origins. Before registry read, the editor's probability of guilt is 1/2. After briefing the registrar also has 1/2. The acquired registry invalidates A, leaving the editor at 1/6 and registrar at 1/2 until any future communication. This follows from the fixed law; trust enables evidence access rather than changing the likelihood of guilt.

## Authoring audit

north_quay_access.swmd.min.md and its sidecar specify a restricted deterministic social-access mechanism slice, distinct from the complete Bayesian session. The same application encounter has reachable grant and refusal reactions; trust changes the winner on both paired perturbations. Every declared ending and reaction is reached and all effects are at most 1/4 without clipping. The slice ends at record acquisition, leaving factual inference to the separate session. Its early-application staging is illustrative and is not identical to session timing. The fixture uses the prior SWMD subset auditor, not a native editor/runtime validation.

The exact session verifier checks every policy against weighted realized-session outcomes in all 42 policy-budget cells, compares the full budget-four policy against a separate decision tree over actual public packets, reverses world order in that tree, and checks public packet equivalence on all 22,464 world-specific action prefixes (16,848 terminal prefixes; 4,056 distinct public histories) at social budget five. Equivalence keys exclude the social response itself and use acquired factual observations, so leaked information in a reaction could be detected. This is a finite structural test, not a general security guarantee. Private grades and hidden world assignment must remain isolated on the evaluator host. The public session packet follows the earlier protocol; live editor and TypeScript integration were not run for this stage.

## Reproduction

From codex-skills/storyworld-building/scripts:

    python -m unittest -q test_provenance_access.py test_provenance_design_audit.py test_provenance_session.py test_provenance_characters.py test_reaction_sensitivity.py
    python verify_provenance_access.py --output /tmp/access_receipt.json
    python provenance_access.py --budget 5

The last command is JSONL; send e.g. {"action":"seals"}. The first command passed 30 tests locally. The full receipt regenerated byte-for-byte. Its SHA-256 and exact summary are committed in access_receipt_summary.json; all detailed metrics, mechanical results, and witness transitions are generated by the verifier. No repository-wide CI was run.

## Next

Introduce multiple social routes with different actors' goals, costs and reliability, and make one route favorable only in a subset of observable histories. Require both paths to be discoverable through coherent authored clues. Audit whether adaptive route selection beats the fixed route heuristic by a meaningful margin before training agents.
