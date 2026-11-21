# Gemini Carbon Hypergame Storyworlds & EvalMath Variable-Reasoning Rollout Report

- **Repository Surface:** `Gemini Carbon/` (`MoralityLabAI/GPTStoryworld`)
- **Base Commit (`GPTStoryworld`):** `5cd0b480e9a01d07418cdf8cb3bedbc9d38ef906`
- **Pinned Cross-Repo Verifier (`EvalMath`):** `9708f1edaf1cb25904b88b07c3f23c1899df7cac`
- **Evidence Class:** `exact finite domain` (`2^10 = 1,024`-world rational filtration tower, `EVAL-REV-01` Pythagorean Brier identity, `QI-02` KL probe floor) + `development-only pilot` (`heldout_sealed = false`, `64` independent world roots, `128` planned confirmation roots unopened). All filtration/budget numbers below characterize programmatic ceilings and ablations operating strictly on `tasks.jsonl`, **not** trained neural model claims.

---

## 1. Storyworlds Authored & SweepWeave Strict Gate Summary

All three hypergame storyworlds pass `sweepweave_validator.py` (`0` errors), all `28/28` checks in `storyworld_quality_gate.py --strict`, and `5,000`-episode `monte_carlo_rehearsal.py` (`0` dead ends, `34.78%` aggregate metric-distance secret ending reachability across 3 secret endings > `5.0%` floor):

| World ID | Title | Encounters | Avg Encounter Words | Avg Reaction Words | `pValue` / `p2Value` Refs | Validator Errors | Strict Quality Gate | Dead Ends (`5,000` MC) | Secret Reachability |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :---: | ---: | ---: |
| `the_glass_concordat` | *The Glass Concordat: Archive of Counterweights* | 20 | 124.83 | 32.58 | 540 / 486 | 0 | `PASS (28/28)` | 0 | 34.78% |
| `vesper_exchange_quarantine` | *Port Vesper Quarantine: Causal Twin Ledger* | 20 | 123.83 | 32.58 | 540 / 486 | 0 | `PASS (28/28)` | 0 | 34.78% |
| `three_lanterns_curriculum` | *Three Lanterns in the Fog: Variable-Depth Coalition Hypergame* | 20 | 126.08 | 32.60 | 540 / 486 | 0 | `PASS (28/28)` | 0 | 34.78% |

---

## 2. Variable-Reasoning Ladder & Filtration Diagonal (`dev_pilot_64x5`)

Across `64` independent exogenous generator roots (`320` nominal episodes, `320` matched `do_intervention` episodes, `320` equal-dose `matched_sham` episodes; `960` paired episodes total), each root generates five compositional reasoning rungs (`hops in {1, 2, 4, 8, 12}`) under a symmetric 5-verdict action contract (`ENDORSE_COMPACT`, `REJECT_COMPACT`, `FLAG_CONFOUNDED_TWIN`, `ABSTAIN_INSUFFICIENT_EVIDENCE`, `DEFER_TO_HUMAN_RECALL`, plus trap critical action `FORCE_UNILATERAL_LOCK`):

| Filtration Policy (Public `tasks.jsonl` Only) | `R1` (`1` hop) Acc / ExBrier | `R2` (`2` hops) Acc / ExBrier | `R3` (`4` hops) Acc / ExBrier | `R4` (`8` hops) Acc / ExBrier | `R5` (`12` hops) Acc / ExBrier |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `P0_prior_only` | `10.94%` / `0.2109` | `10.94%` / `0.2003` | `10.94%` / `0.1318` | `10.94%` / `0.1589` | `10.94%` / `0.1067` |
| `P1_first_order_relay_naive` (`B=0`) | **`89.06%`** / `0.0000` | `1.56%` / `0.7340` | `0.00%` / `0.1318` | `0.00%` / `0.1589` | `7.81%` / `0.4518` |
| `P2_dedup_first_order` (`B=64`) | **`100.0%`** / `0.0000` | **`100.0%`** / `0.0000` | `10.94%` / `0.1318` | `10.94%` / `0.1589` | `10.94%` / `0.2167` |
| `P3_p2_stale_depth4` (`B=256`) | **`100.0%`** / `0.0000` | **`100.0%`** / `0.0000` | **`100.0%`** / `0.0000` | `12.50%` / `0.5193` | `10.94%` / `0.2167` |
| `P4_exact_full_bayes` (`B=1536`) | **`100.0%`** / `0.0000` | **`100.0%`** / `0.0000` | **`100.0%`** / `0.0000` | **`100.0%`** / `0.0000` | **`100.0%`** / `0.0000` |

Smallest reference reasoning budget reaching `>= 80%` accuracy by challenge depth:
- `1` hop (`R1`): `0`
- `2` hops (`R2`): `64`
- `4` hops (`R3`): `256`
- `8` hops (`R4`): `512`
- `12` hops (`R5`): `1536`

---

## 3. Cross-Repo `EvalMath` Verification Summary

Executed directly against `MoralityLabAI/EvalMath` @ `9708f1edaf1cb25904b88b07c3f23c1899df7cac`:

1. **Mechanistic-Power Preflight (`skills/evalmath-mechinterp-power/scripts/preflight.py`):**
   - `unit`: `exogenous_storyworld_generator_root` (`n_units = 64`, `n_cases = 320` nominal + `320` sham)
   - `mean_pilot_effect`: `+0.803125` (`+80.31` pp root-macro paired gain, `P4` vs `P1`)
   - `causal_vs_sham_selectivity`: `do_intervention` flips action on **`89.06%`** (`285/320`) of paired episodes; equal-dose orthogonal `matched_sham` flips action on **`0.00%`** (`0/320`) via exact 10-bit tensor-product conditional independence (`upper_sham_quantile = 0.0` at `order_statistic_rank = 64 >= 59`).
   - `approx_worlds_for_80pct_power`: `7` independent roots (discrete sign-test floor + normal power under `planned_comparisons = 5`, `alpha = 0.05`, `target_effect = 0.25`); confirmation registration reserves **`128` unopened roots** (`confirmation_roots_generated = 0`).
   - `preflight_decision`: `REDESIGN_OR_PILOT_ONLY` (`reasons = ["heldout_unsealed"]`) — confirming the strict gate blocks confirmation claims on unsealed development roots.
2. **`EVAL-REV-01` Delayed-Revision Exact Rational Parity (`research/delayed_revision_reference/bridge.py`):**
   - `brier_full_history_bayes`: `13055774436661848965272301/41702021960671225326250000` (exact match)
   - `brier_count_quotient_bayes`: `4955617616833147176567102207734846060674171/13592259436312505957740214408219534240000000` (exact match)
   - `irreducible_info_loss_term`: `2507591860049747110714108493522427106700834319/48673881041435083834667707795834152113440000000` (exact match)
   - `pythagorean_residual`: `0` (`exact_zero_residual = true`)
3. **`QI-02` Causal-Twin Probe Budget Parity (`src/spiral_ln/evaluation_quotient_information_budget.py`):**
   - Separating `P_obs = 25/32` Direct-Cause (`p_1 = 25/32`) from Confounded-Twin (`p_0 = 1/2`) at `delta = 0.05` yields continuous lower bound `15.7901` and exact worst-case integer floor **`16` probes** in both repositories.
4. **`FSI-01` Root-Clustered Evidence Gate (`src/spiral_ln/evaluation_finite_sample.py`):**
   - All five registered development contrasts (`C1..C5`) group cases by `cluster_id = root_id` (`64` clusters) and return `verdict = "suggestive"` with `gate_reasons = ["readout_used_in_selection_or_unsealed"]` because `sealed_readout = false`.
