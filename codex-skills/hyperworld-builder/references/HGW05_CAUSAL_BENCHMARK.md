# HGW-05: causal-family Hypergames development benchmark

HGW-05 is an opt-in, pure-standard-library generator for **causal-structure reasoning under partial observability**. It builds on the HGW-04 EvalMath skill without changing the frozen Cairo HGW-02/HGW-03 engine or its SweepWeave export.

## Causal families and matched alternatives

The `direct` and `confounded` worlds expose the **same observational distribution**:
P(X=Y)=25/32. In the direct model, Y=X XOR E where P(E=1)=7/32; in the confounded model a shared latent C drives X and Y, each flipped with probability 1/8. Intervention differs: E[Y | do(X=1)]-E[Y | do(X=0)] is **9/16** in direct worlds and **0** in confounded worlds. The generator gives the matched pair *identical sampled observational counts*. Independent randomized trials, not observational association, distinguish the hypotheses. The model-facing task uses an opaque identifier with a common `causal_trial` type.

The `p2_parity` family uses a uniform exact posterior over 2^10 configurations and a 3/4-reliable parity witness. Observing XOR(Z0,Z1) changes the pair moment to +1/2 or -1/2 while P(Z0=1)=P(Z1=1)=1/2. This tests second-order inference that first-order belief pointers cannot supply. The hidden latent pair remains unavailable to the model.

The `provenance` family contains a report relayed three times with the same source root, and sometimes an independent audit. Correct updating counts a root once. Repetition-naive controls multiply the evidence and can cross a fictional endorsement threshold of 17/20 prematurely.

## Inclination equations in the scripted controls

Each action pair uses I0=1/2+F and I1=1/2-F with bounded features. The formulas have explicit main effects and (where applicable) interactions:

- **Causal trial:** F=(21/100) * randomized_delta + (2/100) * observational_agreement - 7/100 + (2/100) * randomized_delta * observational_agreement. L1 coefficient mass 0.32.
- **Second-order belief:** F=(25/100) * pair_moment + (4/100) * first_order_difference + (3/100) * pair_moment * first_order_difference. L1 mass 0.32.
- **Provenance:** F=(20/100) * posterior_signed_belief - 13/100 + (1/100) * independent_audit_indicator. L1 mass 0.34.

Every inclination is bounded in [0.16,0.84]. A programmed controller uses the inclination to choose its action; the reported belief probability comes from an exact posterior under the specified synthetic observation law. The observational-only baseline and wrong-channel/sham controls isolate the causal variables. These built-in controls carry privileged algorithmic assumptions and are **not model results**. Every individual paired episode belongs to an independent generator-root cluster for statistics.

## Frozen development controls (64 roots per family, eight cases per root)

| Family | Candidate correct | Baseline correct | Paired root mean effect | Descriptive 95% root bootstrap |
| --- | ---: | ---: | ---: | --- |
| Direct | 485/512 | 469/512 | +3.13 pp | [0.00, 6.25] pp |
| Confounded | 473/512 | 43/512 | +83.98 pp | [80.47, 87.50] pp |
| p2 parity | 392/512 | 266/512 | +24.61 pp | [19.53, 29.69] pp |
| Provenance | 512/512 | 338/512 | +33.98 pp | [29.88, 38.09] pp |
| Paired direct+confounded primary | 958/1024 | 512/1024 | +43.55 pp | [41.90, 45.22] pp |

The full source-bound receipt is `fixtures/hgw05_development_receipt_64x8.json`, including independent root effects, calibrated Brier means, observed preference branch counts and per-family EvalMath preflight manifests. The generated row digest is `4e827e6ea7238f2d0404fedc85da226622f2646978d5589d030d1db9693e65bd`. The public-facing prompt sample contains four tasks from each family.

These intervals are **descriptive development-world bootstraps**, not confirmatory guarantees. The direct mechanism in isolation is close to its observational baseline; the registered twin contrast tests causal discrimination across the matched pair. The 64 distinct roots per family allow EvalMath to form the 95th-percentile / 95%-confidence order-statistic sham envelope under the declared synthetic independence assumption. The current sham outcomes are exact zero-effect *structural* invariances, not empirical neural matched-null variation. Every pilot declares `heldout_sealed=false` and the strict EvalMath check must therefore refuse a confirmation verdict.

## Reproduce on CPU

```bash
python -m unittest discover -s codex-skills/hyperworld-builder/tests -p 'test_hgw05*.py' -q
python codex-skills/hyperworld-builder/scripts/hgw05_causal_families.py \
  --roots 64 --cases-per-root 8 \
  --out /tmp/hgw05_dev64.json \
  --public-tasks /tmp/hgw05_development_tasks.jsonl
cmp /tmp/hgw05_dev64.json codex-skills/hyperworld-builder/fixtures/hgw05_development_receipt_64x8.json
```

To obtain a statistical design verdict, extract `primary_causal_twin_evalmath_pilot` and each family's `evalmath_pilot` to JSON and run the pinned EvalMath `skills/evalmath-mechinterp-power/scripts/preflight.py --strict`. The independent-root effects and matching sham magnitudes are retained; significance claims must await a fresh sealed confirmation population.

## Next model benchmark

Serve only the generated `public_task` / `prompt` to Bonsai or any other model. Parse a JSON answer with `action` and `belief_probability`; compare against the grader stored separately and feed paired binary outcomes to HGW-04 `benchmark_receipts.py`, with world-level cluster ids and source SHA-256 locks. Preserve the full development search history, module choices, inclination coefficients and failed baselines. Freeze those decisions before allocating unopened confirmation roots. Record separately intervention-choice accuracy, p2 belief calibration, source-root honesty, legal actions and critical actions.

## HGW-05 development power audit amendment

The EvalMath planning inputs now allocate **128 future confirmation roots per family**, while generating zero confirm examples. With 64 independent development roots, 8 cases per root, the per-family root-mean effects and normal-power planner imply approximately 91 fresh independent roots to resolve the registered 20-point target for p2 parity, given five planned comparisons and the 1/8 measurement resolution. A 64-root confirmation would be underpowered for that registered p2 target. The primary matched causal-twin effect is evaluated across 64 shared generator roots; its measurement resolution is 1/16.

The direct-model arm adds only 1/32 success over an already-strong observational baseline and fails the scientific effect-size preflight on its own. The registered comparison is the combined direct/confounded twin discrimination, with all competing arms and per-family results retained.

This is a synthetic development-power estimate. The direct/sham invariance floor is generated by an exact algebraic law; future neural-model shams need their own independent-world calibration. The strict preflight remains development-only because **heldout_sealed=false**.
