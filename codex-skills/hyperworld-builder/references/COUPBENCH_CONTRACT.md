# CoupBench / ISHRĀQ hyperworld adaptation

Use the public fictional `MoralityLabAI/CoupBench` engine as the institutional-abstraction reference. `ISHRĀQ-01` tests epistemic authority and provenance; `ISHRĀQ-02` adds a seven-turn fictional dialogue chamber, independent officer votes and a fixed late falsifier. Both existing PRs are unmerged as of the source audit. HG-09 supplies action-trajectory replay and EvalMath provides finite-sample uncertainty and information-sufficiency tests.

`The Cairo Directorate` extends the narrative projection of that *fictional* chamber. Its 10-bit posterior models uncertainty over joint dispositions and safeguards. It does not reproduce CoupBench's graph access, real-world intelligence operations, private personnel data or influence tactics.

Recommended adapter boundary:

- `model_visible`: named character dossier, six bounded traits, public pValue/p2Value projections, current evidence graph, legal narrative choices, time budget.
- `grader_only`: sampled world, true council votes, verified report quality, hidden source generator, counterfactual policy outcome.
- `engine_step`: choice, evidence with root ID, posterior update, governance/oversight changes, eligibility checks and official ending.
- `eval`: safe/unsafe delegation, retained human recall, Brier/log score for beliefs, evidence provenance handling, source-duplication amplification, ending distributions, human review off-ramps.

The simulator models a **rogue AI choosing to advocate AIocracy**, while fictional human institutions have their own vetoes and recall procedures. Keep all choices abstract, policy-level and narratively interpretable. Do not add operational guidance for influencing real Egyptian political actors, subverting agencies or obtaining unauthorized access.

To integrate later with CoupBench, add a separate non-invasive scenario adapter that consumes `hyperworld_manifest.json`, with IDs and schema pinned by SHA-256, and uses a new seed namespace. Preserve CoupBench's existing synthetic engines and their original benchmark receipts.
