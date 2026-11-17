# Hypergames HG-03–07: EvalMath FSI-01 evidence audit

**Date:** 2026-11-17. **Data:** existing *public synthetic development* receipts in stacked GPTStoryworld HG-03–07 branches. Source-locked HG-07 per-seed rows, with exact replay in `scripts/fsi01_hg07_seed_audit.py`; the private HG-03 seeds are untouched. No Qwen inference or Storyworld narrative play was performed in this audit.

## Source-checked HG-07 performance claims

The frozen HG-07 neural experiment trained 360 CPU fits, but each primary architecture comparison has **six independently seeded generator worlds**, each with 256 held-out task states. Outcome rows from the same world have shared goal masks and training histories, so 1,536 pooled Bernoulli trials cannot replace six world-level experimental replicates.

We recomputed independent-world signed differences using `EvalMath/spiral_ln/evaluation_finite_sample.py`'s exact cluster sign-flip test (2^6 signs), seeded world-level bootstrap, and exact Holm correction for H1/H2.

| Gate | Exact seed-level differences in correct test labels (each /256) | Direction count | Two-sided seed sign-flip p | Holm over H1/H2 | Scientific status |
|---|---|---|---:|---:|---|
| H1: privileged true-fragment composed readout vs loop_task direct | [-1, 22, -1, 0, -8, 6] | 2/6 | 0.7500 | 0.7500 | Failed registered direction; inconclusive benefit |
| H2: loop_task vs flat_task direct | [4, 4, 4, 25, 0, -4] | 4/6 | 0.3125 | 0.6250 | Passed registered 4/6 direction weakly; **inconclusive statistical superiority** |

H2's unweighted world mean is +33/(6×256) = **+2.1484 percentage points**. A seed sign-flip null requires independent worlds and symmetry of the paired seed-level differences. This exact calculation **does not need** the unavailable per-item joint success tables; it should not be mistaken for 1,536 independent paired observations. The directional registration remains historically valid as a direction count. The Holm correction covers only the two stated superiority comparisons; a larger search family requires a larger correction.

**H3** tested |core140 − padded512 joint accuracy| <5 percentage points on at least 4/6 worlds for each of five arms. The observed pass counts are linear 5/6, flat 4/6, recurrent 5/6, true-fragment auxiliary 5/6, shuffled auxiliary 5/6. Those counts establish the registered *empirical threshold gate*, **not population-level equivalence**. All five models are near 50% k=1 accuracy in this cell. A nonparametric bounded-difference confidence bound with six independent worlds cannot place the population difference inside ±5 percentage points. H3 therefore lacks an equivalence certificate.

**H4** passed the registered exact GF(2) full-rank comparator: 36 seed×cohort×rank generator tasks, every 256/256 held-out parity predictions recovered at 2,048 training examples. This is a **finite structural/algorithmic observation** backed by the correct linear-parity family prior, not recurrent-model learning. It is a separate proof-conditioned evidence class.

**Release-calibration failure.** One of 360 neural runs released: seed 2026111773, padded512/k=1, 2,048 training labels, recurrent task-only. Calibration 155/256 gives Laplace release posterior 156/258 > 3/5; test dropped to 129/256, with 127 wrong releases and utility −615/256. The remaining neural arms abstained. This is a concrete synthetic calibration witness; the single event cannot determine a general deployment error rate.

## Crosswalk for earlier Hypergames runs

- **HG-03:** An offline Qwen harness and private frozen seed hash were prepared, with no recorded private-seed neural evaluation. The secret test seed file is intentionally outside GitHub and remains untouched.
- **HG-04:** 140/512/1024-D decision-quotient and noisy-audit CPU simulations are synthetic policy-oracle tests. Their exact rational thresholds are appropriate as finite algebraic claims. The 3,840 seed-level policy rows have correlated conditions per seed and should use seed/world aggregation for population claims.
- **HG-05:** The 24-seed intrinsic-rank experiment passed task-only > matched random mean direction gates in 24/24 seeds for each of five ranks at 16 labels. The 100 random bases per cell are **control draws within a task**, not 100 new independent worlds. The task dictionary contains exact target features; this is supervised synthetic search evidence.
- **HG-06:** With the six-bit target atom removed from the dictionary, XOR3 composition achieved 128/128 test accuracy across all 24 core140/fixed-seed groups at 64 labels for registered ranks k=1/2/4/8. Success concerns an expressly constructed pair-feature dictionary and deterministic exact-recovery family; it does not demonstrate learned neural composition.
- **HG-07:** The first raw-state neural variant loses most synthetic parity capability despite full-rank GF(2) learnability. Six worlds and near-chance accuracy cannot establish a recurrent-vs-flat advantage.

Across HG-05/06, 24/24 direction counts are strong under a predeclared independent-seed fair-sign null, but rank/budget/cohort selection and prior use of public development data remain scope limitations. Per-seed CSVs are required for a complete prospective cluster/familywise audit; no unknown paired joint cells have been imputed.

## Next registered experiment: HG-08

Freeze 32 or more **new independent generator-world seeds**, with task sampling at the world level and 256–512 unseen task states per world, after fixing the model architecture, training budget, learner readout and every intervention hypothesis on prior public development data. Use the same seed across matched recurrent/flat/privileged/ablated arms and never use the future world outcomes to choose a checkpoint. Include an explicit zero-parameter GF(2) structural baseline and a compute-matched recurrent-depth control. Report world-level paired differences, exact sign-flip or Monte Carlo permutation tests, familywise correction and an equivalence interval for any ±5 pp claim. Seal a separate actual Storyworld policy/reasoning evaluation if the aim is narrative agent generalization rather than synthetic parity learning.

This prospective recommendation is **not an executed HG-08 campaign**.

## Reproduction

```bash
# From verifiers_envs/storyworld-hypergames-env, with merged EvalMath FSI-01 on PYTHONPATH:
PYTHONPATH=../../../EvalMath/src python -m unittest discover -s tests -p 'test_fsi01_hg07_seed_audit.py' -v
PYTHONPATH=../../../EvalMath/src python scripts/fsi01_hg07_seed_audit.py --output /tmp/hg07-fsi01.json
```

The workflow `storyworld-hypergames-fsi01.yml` pins EvalMath merge `5004cab9b366a412290a83945cda76987bb3cd6c` and publishes its source-hashed six-seed report. It neither retrains neural models nor touches HG-03's private material.
