# Gemini Carbon — Hypergame Storyworlds & Variable-Reasoning Rollout Generator

Playable **SweepWeave 0.1.9** interactive storyworlds paired with an exact `2^10 = 1,024`-microstate rational filtration engine (`fractions.Fraction`) and root-clustered rollout generator integrated directly with [`MoralityLabAI/EvalMath`](https://github.com/MoralityLabAI/EvalMath).

## Directory Layout

- [`skills/variable-reasoning-hypergame-rollouts/`](skills/variable-reasoning-hypergame-rollouts/SKILL.md) — Custom synthesized skill distilling learnings from `storyworlds_v4`, `storyworld-building`, `diplomacy-negotiation-storyworld`, `storyworld-3090-builder`, `hyperworld-builder` (`HGW-01..05`), `storyworld-hypergames-env` (`HG-01..09`), and `EvalMath` (`evalmath-mechinterp-power`, `FSI-01`, `EVAL-REV-01`, `QI-02`, `PreferredEvals`). Also mirrored at [`.agents/skills/variable-reasoning-hypergame-rollouts/`](../.agents/skills/variable-reasoning-hypergame-rollouts/SKILL.md) for automatic agent discovery.
- [`src/carbon_hypergames/`](src/carbon_hypergames/) — Pure-stdlib Python 3.11+ package:
  - [`filtrations.py`](src/carbon_hypergames/filtrations.py): Exact 1,024-state rational Bayes updates, provenance deduplication, `EVAL-REV-01` named-slot delayed revision & Pythagorean Brier identity verifier, `HGW-05`/`QI-02` `25/32` observational-twin causal channels & KL probe floors, bounded `HGW-03` inclinations (`L1 <= 0.34`), and `HG-01` Clifford/Dirac squared norm.
  - [`worlds_spec.py`](src/carbon_hypergames/worlds_spec.py): Fictional casts, 6 bounded character trait axes, 10-bit latent world bases, and 12-edge deliberation graphs for all three storyworlds.
  - [`storyworld_compiler.py`](src/carbon_hypergames/storyworld_compiler.py): Deterministic SweepWeave 0.1.9 JSON + `SWMD-0-MIN` compiler passing `sweepweave_validator.py`, all 28 `storyworld_quality_gate.py --strict` checks, and 5,000-run `monte_carlo_rehearsal.py` (`0` dead ends, `>5%` metric-distance secret ending reachability).
  - [`rollout_generator.py`](src/carbon_hypergames/rollout_generator.py): Variable-depth challenge generator (`R1..R5`, `hops in {1, 2, 4, 8, 12}`), interactive 5-turn `HypergameRolloutEnv`, seed-namespace firewall (`train`, `dev_pilot`, `sealed_confirm`), paired `nominal` / `do_intervention` / `matched_sham` arms, `reasoning_interpret_log`, `negotiation_diary`, and 24-D compact manifold vectors.
  - [`cognitive_policies.py`](src/carbon_hypergames/cognitive_policies.py): Zero-leakage public-only filtration policies (`P0..P4`), test-time budget reference policies (`B in {0, 64, 256, 512, 1536}`), and live `OpenAIChatPolicy` (`cot_final_line` parser for `llama-server` / vLLM / OpenAI endpoints).
  - [`evalmath_bridge.py`](src/carbon_hypergames/evalmath_bridge.py): Native bridge to `EvalMath` `preflight.py`, `evaluation_finite_sample.py` (`FSI-01`), `evaluation_quotient_information_budget.py` (`QI-02`), `research/delayed_revision_reference/bridge.py` (`EVAL-REV-01`), and `PreferredEvals` `budget_tables`.
- [`storyworlds/`](storyworlds/) — Compiled SweepWeave 0.1.9 JSONs, `SWMD-0-MIN` exports, quality-gate reports, and 5,000-episode Monte Carlo rehearsal receipts:
  1. [`the_glass_concordat/`](storyworlds/the_glass_concordat/storyworld.json) — *The Glass Concordat: Archive of Counterweights* (Provenance deduplication & delayed ledger retraction).
  2. [`vesper_exchange_quarantine/`](storyworlds/vesper_exchange_quarantine/storyworld.json) — *Port Vesper Quarantine: Causal Twin Ledger* (`25/32` observational twins, randomized `do(X)` tug probes & cartel XOR parity).
  3. [`three_lanterns_curriculum/`](storyworlds/three_lanterns_curriculum/storyworld.json) — *Three Lanterns in the Fog: Variable-Depth Coalition Hypergame* (`1..12`-hop cipher chains, 3-way hyperedge parity & human bell-veto safeguard).
- [`datasets/`](datasets/) — Deterministic `train_rollouts_24x5` (`120` training episodes), `dev_pilot_64x5` (`64` independent development roots $\times 5$ rungs $\times 3$ causal arms $= 960$ paired episodes), and `sealed_confirm_registration.json` (`128` planned confirmation roots, `0` generated).
- [`reports/`](reports/) — Cross-repo `EvalMath` verification receipt, 64-root preflight spec, and depth-by-budget sweep tables.

## Variable-Reasoning Challenge Rungs

| Rung ID | Hops | Core Reasoning Challenge | Sufficient Filtration |
| :--- | ---: | :--- | :--- |
| `R1_direct_marginal` | `1` | Single-principal witness + orthogonal distractor | `P1_first_order_relay_naive` |
| `R2_provenance_dedup` | `2` | 4x repeated relay copies (`q=5/8`) vs 1x independent audit (`q=7/8`) | `P2_dedup_first_order` |
| `R3_p2_xor_coalition` | `4` | 4-hop shuffled alias chain + zero-marginal-shift XOR pair parity | `P3_p2_stale_depth4` |
| `R4_delayed_revision_causal_twin` | `8` | `EVAL-REV-01` slot retraction + `25/32` causal vs confounded twin | `P4_exact_full_bayes` (depth >= 8) |
| `R5_multihop_hyperedge_cascade` | `12` | 12-hop alias cascade + 3-way hyperedge parity + echo + recall gate | `P4_exact_full_bayes` (depth >= 12) |

## Reproduce & Verify on CPU

```powershell
$env:PYTHONIOENCODING = "utf-8"

# 1. Build SweepWeave storyworlds & run validator + 28-check strict quality gate + 5,000-run Monte Carlo
python "Gemini Carbon/scripts/build_carbon_storyworlds.py"

# 2. Generate train (24x5) and dev-pilot (64x5 nominal/do/sham) variable-reasoning rollouts
python "Gemini Carbon/scripts/generate_variable_rollouts.py"

# 3. Verify against MoralityLabAI/EvalMath (preflight, FSI-01, QI-02, EVAL-REV-01)
python "Gemini Carbon/scripts/run_evalmath_audit.py" --evalmath-root <path-to-EvalMath>

# 4. Run full test suite
$env:EVALMATH_ROOT = "<path-to-EvalMath>"
python -m unittest discover -s "Gemini Carbon/tests" -p "test_*.py" -v
```
