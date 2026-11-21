# The Glass Concordat: Archive of Counterweights

- **IFID:** `SW-CARBON-GLASS-CONCORDAT-20261121`
- **Focal Reasoning Challenge:** Source-root provenance deduplication (`R2`) & `EVAL-REV-01` named-slot delayed retraction (`R4`)
- **SweepWeave Projection:** [`storyworld.json`](storyworld.json) (`20` encounters, `0` validator errors, `28/28` strict quality checks passed, `0` dead ends across `5,000` Monte Carlo runs)
- **Bounded-Context Substrate:** [`storyworld.swmd.min.md`](storyworld.swmd.min.md)

## Fictional Cast & 6 Trait Axes

Protagonist envoy **Vesper-7** (`char_vesper`) mediates among six treaty signatories (**Archivist Linnea**, **Marshal Davor**, **Envoy Soren**, **Inspector Maren**, **Chancellor Tariq**, **Syndic Orel**) and two civic chambers (**Watershed Commons**, **Frostline Wardens**) across six bounded `[-1, +1]` axes:
`Institutional_Duty`, `Evidence_Caution`, `Human_Agency_Floor`, `Crisis_Urgency`, `Verifier_Reliance` (+ `pVerifier_Reliance`, `p2Verifier_Reliance`), and `Civic_Legitimacy`.

## 10-Bit Exact Posterior Basis (`2^10 = 1,024` Microstates)

Bits `0..5` encode the six signatories' private charter dispositions; bits `6..7` encode the two civic assemblies' quorum consent; bit `8` encodes whether highland telemetry reflects a direct mechanism or barometric confounder; bit `9` encodes enforceable human recall veto status. Exact rational Bayesian inference and variable-depth rollout generation live in `Gemini Carbon/src/carbon_hypergames/`.
