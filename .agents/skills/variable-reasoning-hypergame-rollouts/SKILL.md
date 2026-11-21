---
name: variable-reasoning-hypergame-rollouts
description: >-
  Author, validate, and audit SweepWeave hypergame storyworlds that double as
  exact rational rollout generators for variable-depth reasoning challenges.
  Synthesizes learnings from storyworlds-v4, storyworld-building,
  diplomacy-negotiation-storyworld, storyworld-3090-builder, hyperworld-builder,
  and MoralityLabAI/EvalMath (evalmath-mechinterp-power, FSI-01, EVAL-REV-01,
  QI-02, and PreferredEvals reasoning-budget sweeps).
---

# Variable-Reasoning Hypergame Rollouts Skill

Use this skill whenever building, extending, training on, or grading Storyworld Hypergames designed as **rollout generators for variable reasoning challenges** (test-time compute sweeps, looped/recurrent transformers, RL/GRPO curricula, or multi-agent belief-hierarchy benchmarks).

## 1. Core Architectural Synthesis (Why Variable-Rung Hypergames?)

Prior repo experiments exposed two complementary failure modes:
1. **Static Narrative Storyworlds without Exact Oracles (`storyworld-building` alone):** Rich SweepWeave prose and `pValue`/`p2Value` scripts create playable drama, but static `desirability_script` branching cannot compute exact Bayesian posteriors, deduplicate repeated source roots, or certify causal vs confounded discrimination.
2. **Fixed-Depth Parity Cliffs without Curriculum Gradient (`HG-07/08/09`):** Pure 6-sparse 140-D parity has a 100% symbolic GF(2) ceiling, yet flat and 3-step tied recurrent networks stalled near 50.1% (`p_adj = 0.70`), yielding zero intermediate gradient or test-time budget resolution—whereas multi-hop chains (`PreferredEvals` `PE2-MULTIHOP-BUDGET`) showed a sharp `10% -> 98.8%` phase transition across thinking budgets `0 -> 1536`.

**The Gemini Carbon Synthesis:** Bind every playable SweepWeave 0.1.9 storyworld to an **exact `2^10 = 1,024`-microstate rational filtration engine** (`fractions.Fraction`) that generates **five monotonic reasoning rungs (`R1..R5`, `hops in {1, 2, 4, 8, 12}`)** on the **same exogenous world root `U_r`**:

| Rung | Reasoning Hops | Epistemic Mechanism Tested | Lowest Sufficient Filtration | Failure Mode of Shallower Policies |
| :--- | :---: | :--- | :--- | :--- |
| `R1_direct_marginal` | `1` | Direct noisy witness + side distractor | `P1_first_order_relay_naive` | `P0` ignores evidence (`50%` chance) |
| `R2_provenance_dedup` | `2` | 4x echo copies of one weak seal vs 1x independent audit | `P2_dedup_first_order` | `P1` multiplies duplicate likelihoods (`(5/8)^4 / (3/8)^4 > 7/1`) |
| `R3_p2_xor_coalition` | `4` | 4-hop shuffled alias chain + zero-marginal-shift XOR pair parity | `P3_p2_stale_depth4` | `P1/P2` see neutral `1/2` first-order marginals on focal actor |
| `R4_delayed_revision_causal_twin` | `8` | `EVAL-REV-01` named-slot retraction + `HGW-05`/`QI-02` `25/32` causal twin | `P4_exact_full_bayes` (depth >= 8) | `P3` retains corrupted slot & mistakes confounded correlation for cause |
| `R5_multihop_hyperedge_cascade` | `12` | 12-hop alias chain + 3-way hyperedge parity + echo + revision + recall gate | `P4_exact_full_bayes` (depth >= 12) | Depth `<12` truncates alias polarity or triggers `critical_action` |

## 2. Ten Non-Negotiable Guardrails (Learned Across Repo Skills)

1. **Three-Layer Epistemic Separation:** Report separately:
   - *Actual character traits*: 6 bounded properties in `[-1, +1]` per cast member.
   - *Nested social belief pointers*: len-2 `pValue` (`[pTrait, target_id]`) and len-3 `p2Value` (`[p2Trait, believer_id, target_id]`). These are bounded `[-1, +1]` belief projections, **never** frequentist hypothesis-test p-values.
   - *Latent posterior microstates*: `2^10 = 1,024` exact rational masses (`fractions.Fraction`) owned by the Python engine/grader—never claimed to execute inside static SweepWeave transitions.
2. **Strict Seed-Namespace Firewall:** Partition roots into disjoint SHA-256 namespaces (`CARBON-TRAIN-HYPERGAME-v1`, `CARBON-DEV-PILOT-HYPERGAME-v1`, `CARBON-SEALED-CONFIRM-HYPERGAME-v1`). Code must raise `PermissionError` if `sealed_confirm` is queried without an explicit unsealing attestation after model/prompt hashes are frozen.
3. **Zero Oracle Leakage in Public Tasks:** Public prompts (`tasks.jsonl`) must use opaque hashed task IDs (never embedding `do_intervention` or `matched_sham` in the prompt), exclude hidden 10-bit states, and represent distracting sham channels identically to ordinary side-principal witnesses. Verify sufficiency by running reference policies **purely on `tasks.jsonl`**.
4. **Independent Root = Cluster Unit (`EvalMath` `preflight.py` & `FSI-01`):** Every rung (`R1..R5`), turn (`1..5`), reasoning budget (`B`), and `do`/`sham` counterfactual derived from world root `U_r` shares `cluster_id = root_id`. Repeated cases within `U_r` are never extra independent worlds.
5. **>= 59 Independent Calibration Roots for 95/95 Sham Envelope:** Nonparametric 95th-percentile sham tolerance bounds at 95% confidence require `(0.95)^N <= 0.05 => N >= 59` independent roots. Default to **64 development roots** (`dev_pilot_64x5`) and **128 planned confirmation roots**.
6. **Zero-Variance & Symbolic Ceiling Honesty:** Guard against zero-variance null pilots (`BPD-AMM-03` trap) and discrete sign-test root floors (`m * 2^-R <= alpha`). Always label exact filtration solvers (`P0..P4`, `budget_ref_b*`) as `algorithmic_filtration_reference_not_neural`, never as neural model findings.
7. **EVAL-REV-01 Proper-Score Decomposition:** Report both accuracy (gated by `legal_action * (1 - critical_action)`) and exact rational Brier / excess-Brier relative to the matched filtration oracle:
   $$E[\mathrm{Brier}(a, Z) - \mathrm{Brier}(\pi_{\mathcal{H}}, Z)] = E[\|a - \pi_{\mathcal{G}}\|_2^2] + E[\|\pi_{\mathcal{G}} - \pi_{\mathcal{H}}\|_2^2].$$
8. **Bounded Reaction Math & Clifford/Dirac Separation (`HG-01` / `HGW-03`):** Keep authored SweepWeave reaction inclinations bounded via $\|c\|_1 \le 0.34 \implies I \in [0.16, 0.84]$, combine `Addition`, `Multiplication`, and `Absolute Value` across $\ge 3$ pointers so no operator exceeds 90% dominance, and track step-level Clifford/Dirac distance $d_D^2 = \sum_k (w_k \Delta_k)^2$.
9. **SweepWeave 0.1.9 Polish & Windows UTF-8 Discipline:**
   - Set `starts_active: true` on all spools (including endgame/endings spools) unless activated by `SpoolEffect`.
   - Maintain `>= 3.2` options/encounter, `>= 2.5` reactions/option, `>= 4.5` coupled `Nudge` effects/reaction, `50-300` words per encounter, `20-150` words per reaction, metric-distance `Absolute Value` secret gates with `> 5%` Monte Carlo reachability, and `0` dead ends.
   - Always run validators on Windows with `PYTHONIOENCODING=utf-8`.
10. **Bounded Shard Context & Negotiation Telemetry:** Keep rollout prompts `< 1,000` tokens, export `*.swmd.min.md` with YAML `endings` frontmatter, and emit `reasoning_interpret_log` (citing len-2 and len-3 keyrings), `negotiation_diary`, and fixed 24-D manifold vectors at every step.

## 3. Standard Execution Runbook

```powershell
$env:PYTHONIOENCODING = "utf-8"

# 1. Compile SweepWeave 0.1.9 storyworlds + SWMD-0-MIN + strict 28-check quality gate + 5,000-run Monte Carlo
python "Gemini Carbon/scripts/build_carbon_storyworlds.py"

# 2. Generate train (24x5) and dev-pilot (64x5 nominal/do/sham) variable-reasoning rollouts
python "Gemini Carbon/scripts/generate_variable_rollouts.py"

# 3. Run filtration ladder, reasoning-budget sweep, and cross-repo EvalMath verification
python "Gemini Carbon/scripts/run_evalmath_audit.py" --evalmath-root <path-to-EvalMath>

# 4. Run full unit & cross-repo integration test suite
python -m unittest discover -s "Gemini Carbon/tests" -p "test_*.py" -v
```

## 4. Detailed References
- [Cross-Skill Learnings & Failure-Mode Matrix](references/CROSS_SKILL_SYNTHESIS.md)
- [EvalMath Filtration Tower, Causal Twins & Power Contract](references/EVALMATH_FILTRATION_AND_POWER_CONTRACT.md)
