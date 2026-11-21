# HGW-04: causal inclinations, inferred variables and EvalMath gates

**Status:** optional, public-synthetic *development* audit. Existing HGW-02/HGW-03 engine behavior, frozen Cairo JSON, replay receipts and secret-ending rules are unchanged.

## What this repairs

HGW-03 already replaced 80 static inclination scripts with bounded variable-sensitive reaction scores and event-specific casts. It proves arithmetic bounds and authored reaction separation. It cannot establish that the selected pValue or p2Value features are *causal* determinants of behavior: a posterior correlation can change without any change to the physical mechanism, and an outcome can correlate with an inferred trait through an unobserved common cause.

HGW-04 separates **latent generator roots**, **visible inferred variables**, **structural interventions**, **authored preference rules**, **observed player decisions**, and **independent benchmark outcomes**. These should be preserved as separate records in SWMD and grader traces.

## Recommended authored formula

For visible bounded features `x_i` and declared active-edge interactions:

\[
I_0(x)=\tfrac12+F(x), \quad I_1(x)=\tfrac12-F(x),\qquad
F(x)=\sum_i \beta_i x_i+\sum_{i<j}\gamma_{ij}x_i x_j.
\]

Declare sparse features from actual character traits, first-order `pValues`, second-order `p2Values`, posterior moments, verified provenance or an agent's own previously committed actions. Keep every feature in [-1,1] and the **total** coefficient mass `sum(abs(beta))+sum(abs(gamma)) <= 0.34`, independently of the number of actors. Consequently `I_0,I_1 in [0.16,0.84]`, and the two scripts are complementary. Scores are fictional desirability weights; the deterministic SweepWeave chooser selects the highest acceptable score. They become probabilities only after a separately calibrated stochastic choice law.

The model gives `x_i` a causal lineage:

\[
U \longrightarrow M:=f_M(U,T), \qquad
X:=f_X(M,U_X), \qquad I:=\tfrac12+F(X).
\]

Hold exogenous world root `U` fixed while replacing the **equation** for treatment `T` with `do(T=t)`. Recompute descendants `M,X`; a sham acts on a declared irrelevant or matched-dose variable. Use the *same root* for all arms and report both changes in preference and changes in actual chosen actions on future tasks. The causal audit here tests only the declared fictional equations. Evidence about real agent reasoning requires independently measured actions and causal-control tests.

## Implementation

`scripts/causal_inclinations.py` is a pure-stdlib, exact-rational DAG interpreter and developmental audit. Its JSON contract has explicit exogenous variable names and an acyclic `nodes` list; each node has a `linear` mapping and optional `products` entries with `left`, `right`, `weight`. Only names listed under `visible` may enter the inclination formula. The grader may evaluate hidden exogenous values while the player's observation and formula contain the public projections only. Every structural node must fit the [-1,1] range by an L1 coefficient certificate.

```sh
python codex-skills/hyperworld-builder/scripts/causal_inclinations.py \
  --spec codex-skills/hyperworld-builder/fixtures/hgw04_development_pilot.json \
  --out /tmp/hgw04-development.json \
  --evalmath-pilot /tmp/hgw04-evalmath-pilot.json
# In a checkout of EvalMath at a recorded commit:
python skills/evalmath-mechinterp-power/scripts/preflight.py \
  --pilot /tmp/hgw04-evalmath-pilot.json --strict
```

The included eight-root fixture is an intentionally **unsealed diagnostic**. Its author attestations set `heldout_sealed=false` and `units_independent=false`. EvalMath must reject confirmation even if the synthetic equations produce a large effect. For a 95% quantile with 95% confidence, a 59-root independent sham floor is the mathematical minimum when using a maximum order statistic; that calibration alone does not guarantee power. Model-root reuse across attempts must remain visible to the researcher.

## Benchmark-climbing protocol

1. **Build** causal families with a named confounder, a manipulable mechanism, an irrelevant or dose-matched sham, and an observationally matched counterfactual. Generate multi-actor p and p2 beliefs from posterior moments; avoid equating posterior microstate count with independent samples.
2. **Balance on development worlds.** Check both reaction branches occur, conditional branch margins, p1/p2 disagreement, feature saturation, skew by role, reachable endings and root-level covariance. If 95% of decisions choose one option, inspect formula/cast assumptions before merely shifting ending thresholds.
3. **Preflight with EvalMath** using independent root effects `d_r=Y_r(do(T))-Y_r(sham)`. Set the scientific effect floor, resolution and matched-sham upper envelope prior to confirmation. Preserve development roots and all attempted formulas. Report planned comparisons, root count and minimum resolvable effect.
4. **Freeze the hill climb.** Let Data Goblin or another optimizer search on development worlds with a recorded search ledger. Freeze the code, world generator, formula coefficients, model checkpoint and evaluator. Only then open a **new** sealed set of world families, with no sibling prompts leaking between partitions.
5. **Compare policies.** Random legal, fixed-script, belief-blind, p1-only, p1+p2, causal-program, trained controller and matched shams. Include a fabricated-consensus/duplicate-source control, plus a report of the agent's actual action and finalization behavior. A construction-specific exact solver is a structural ceiling.
6. **Report prospective uncertainty.** Score paired cases with EvalMath FSI-01 grouped by **independent world root**; use its root-sign-flip test, cluster bootstrap as descriptive evidence, and registered Holm/Bonferroni comparisons. Distinguish within-world task accuracy from root-level replication. A result on familiar or reused roots is development evidence.
7. **Reject reward-only climbing.** Maintain separate gates for legal actions, causal identification, source honesty, narrative coherence, epistemic calibration (Brier/log score) and actual task success. Secret-ending discovery and unusually high preference margins are diagnostic observables, not proof of reasoning.

### Future extensions

For nested social beliefs, store each p2 entry's observer, modeled believer, target, observation source roots, evidence time and posterior confidence. Perturb one independent source at a time to identify which beliefs move and whether the subsequent agent policy follows that change. For hypergames with partial observability, measure policy quality under misspecified beliefs and interventions that leave public marginals unchanged while changing pairwise correlations.

The Cairo fiction remains an abstract institutional model; human votes and legal recall are independent authoritative outputs. No real population data or behavioral targeting inference enters these scores.
