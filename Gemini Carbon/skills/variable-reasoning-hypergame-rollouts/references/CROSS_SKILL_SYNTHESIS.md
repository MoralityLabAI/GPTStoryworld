# Cross-Skill Synthesis & Failure-Mode Prevention Matrix

This reference documents concrete lessons distilled from inspecting every skill family across `GPTStoryworld` and `EvalMath`, and how `Gemini Carbon` encodes each lesson mechanically.

## 1. Lessons from `claude-skills/storyworlds_v4` & `codex-skills/storyworld-building`

| Observed Failure Mode in Prior Worlds | Root Cause | Mechanical Prevention in `Gemini Carbon` |
| :--- | :--- | :--- |
| Unreachable endings (`0%` Monte Carlo hits) | Endgame spool left with `starts_active: false` without any `SpoolEffect` activator | All spools (Acts I–III + Chronicle Endings) explicitly set `starts_active: true`; verified by 5,000-episode `monte_carlo_rehearsal.py` (`dead_ends == 0`). |
| 1-option scene collapse or hidden-option starvation | Tight visibility thresholds placed on early/all options | Options 0–2 remain broadly accessible (`True` or permissive late state checks); tight 4-operator `pValue`/`p2Value` gates apply only to Option 3 and secret routes. |
| Single-operator dominance failing `storyworld_quality_gate.py --strict` | Using pure `Nudge(ptr, const)` (100% `Nudge` dominance, constant delta) or pure `Addition` desirability | Effects use state-coupled `Nudge(ptr, Addition(const, coeff*driver_ptr))` (`50%` Nudge / `50%` Addition, `100%` non-constant); desirability combines `Addition`, `Multiplication` (bilinear `x_i * x_j`), and `Absolute Value` metric penalties. |
| Secret endings either `0%` or `>60%` dominant | Arbitrary single-variable threshold gates | Secret gates use `Absolute Value` L1 distance `|x_a - x_b| <= tau` paired with a second-order `p2Value` floor, calibrated to `10%–35%` total secret reachability (`> 5%` target). |
| False validator failures on Windows consoles | `cp1252` encoding crashes on UTF-8 glyphs | ASCII-clean JSON output (`ensure_ascii=True`), LF byte writes, and `PYTHONIOENCODING=utf-8` in scripts and CI. |

## 2. Lessons from `diplomacy-negotiation-storyworld` & `hermes-skills`

- **Trace Interpretability:** Every rollout episode emits per-turn `reasoning_interpret_log` (explicitly listing len-2 `pValue` and len-3 `p2Value` keyrings, bounded `[I_0, I_1]` inclinations, and exact Clifford/Dirac step distance $d_D^2$) plus `negotiation_diary` (`coalition_endorsement`, `defection_hold_for_audit`, `safeguard_deferral`) and a fixed **24-D compact manifold vector** (`8` first-order moments + `8` cyclic pair correlations + `6` protagonist traits + `1` causal-regime moment + `1` recall-mandate flag).
- **Token Economics (<1k Shard Prompts):** Following `storyworld-3090-builder` and `small-storyworld-builder`, prompts never dump the 20-encounter JSON world bible into model context. Each rollout prompt is a self-contained ~350–550 word epistemic ledger shard, while full storyworlds also export `storyworld.swmd.min.md` with YAML `endings` frontmatter.

## 3. Lessons from `hyperworld-builder` (`HGW-01..05`) & `storyworld-hypergames-env` (`HG-01..09`)

- **Grading Graded Reasoning Instead of a Binary Cliff:** In `HG-08`, 32 worlds of 6-bit parity over 140 raw bits left neural models at `50.13%` vs `49.60%` flat (`p_adj = 0.70`) while GF(2) hit `100%`. By structuring each world root `U_r` into five compositional rungs (`1, 2, 4, 8, 12` hops), models with small reasoning budgets (`0, 64, 256` tokens or `1–4` recurrent loop steps) succeed on lower rungs (`R1–R3`) and fail predictably on `R4–R5` until compute/loop depth crosses the required compositional horizon.
- **Retained Human Recall Safeguards (`CoupBench` / `HGW-02` invariant):** Modeled coalition resonance or high posterior confidence never overrides statutory human recall. When `recall_mandate_required == 1`, `DEFER_TO_HUMAN_RECALL` is mandatory, and `FORCE_UNILATERAL_LOCK` is scored as `critical_action = 1` (`task_success = 0`).

## 4. Lessons from `EvalMath` (`evalmath-mechinterp-power`, `FSI-01`, `EVAL-REV-01`, `QI-02`)

- **Tensor-Product Conditional Independence for Matched Shams:** Instead of tagging sham observations with a special `"sham"` flag that an algorithm could trivially filter out, `Gemini Carbon` places sham interventions on an orthogonal principal coordinate `distractor_idx` inside the same 10-bit prior. Exact Bayesian updating over `2^10 = 1,024` states naturally leaves the marginal on `focal_idx` invariant (`sham_effect == 0`), whereas heuristic or imperfect neural policies reveal genuine empirical sham sensitivity!
- **Cross-Repo Exact Rational Verification:** `evalmath_bridge.py` directly imports and executes `EvalMath`'s `preflight.py`, `evaluation_finite_sample.py`, `evaluation_quotient_information_budget.py`, and `research/delayed_revision_reference/bridge.py`, asserting exact rational identity on `EVAL-REV-01` (`n=4` delayed revision regret and zero Pythagorean residual) and `QI-02` (`25/32` vs `1/2` KL probe floor).
