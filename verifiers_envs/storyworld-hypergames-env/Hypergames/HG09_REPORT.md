# HG-09: explicit sparse parity structure and target-bit causal selectivity

**Date:** 2026-11-17. Registered before confirmation data on GPTStoryworld research branch: `f03f658` initially, `2b8ac281` fixed the normalized binary H2 endpoint, and **`90f7b9df` excluded two implementation-smoke worlds** before running the 64 confirmation worlds. Public synthetic data only. HG-03's private seeds and ARG-03's sealed test remain untouched.

## Question

HG-08 showed that raw tied recurrence, one-pass and privileged two-bit auxiliary supervision stayed near chance after 350 AdamW updates on six-bit parity. HG-09 tests the effect of **supplying a correct GF(2) sparse-parity family prior**. Training labels permit binary Gaussian elimination to recover the six active input bits; a deterministic parity circuit then computes their XOR. A sham circuit uses a disjoint six-bit support. This is a deliberately privileged *algorithmic inductive bias* condition. It is not emergent neural structure, learned SAE coordinates, BPD component identification, or evidence about narrative Storyworld agents.

All four arms receive the same 2,048 raw training examples per world. The flat and tied networks have the HG-07 RawNet 64-wide architecture and the same 350 AdamW updates/batches as HG-08. The GF(2) solver uses the parity-family prior and performs separate algebraic work; wall-clock cost is measured. A fresh per-world 256-example calibration determines release and the 256 test labels are accessed only after fitting and calibration. Every world is the unit of inference; 16,384 within-world test cases are not 16,384 independent mechanism replicates.

## Frozen hypotheses and actual local results

| Arm | Correct / 16,384 | Accuracy | Target-bit edit flips prediction AND irrelevant edit preserves it |
|---|---:|---:|---:|
| Raw flat neural | 8,225 | 50.20% | 957/16,384 = 5.84% |
| Raw tied recurrent neural | 8,240 | 50.29% | 963/16,384 = 5.88% |
| GF(2)-compiled sparse parity circuit | **16,384** | **100%** | **16,384/16,384 = 100%** |
| Disjoint scrambled support circuit | 8,213 | 50.13% | 0/16,384 = 0% |

**H1:** compiled circuit minus raw tied recurrent, minimum meaningful difference +0.10. Paired macro effect **509/1024 = +49.70703125 percentage points** across 64 independent generator worlds. EvalMath FSI-01 returns `confirmed` under its stated world-independent, signed-exchangeability assumptions. Bonferroni-adjusted 20,000-signflip Monte Carlo p approximately **0.000100**; conservative independent-world Hoeffding lower bound **+0.1575**, above the predeclared +0.10 floor. The Monte Carlo p is limited by simulation count; it is not the exact 64-world tail probability.

**H2:** causal-selectivity success difference, compiled circuit minus disjoint sham; minimum effect +0.50. Exactly **64/64 worlds** meet 256/256 binary target/irrelevant edit discrimination for the compiled circuit; the disjoint-support sham gets 0/256 on each world. Effect +1.00. FSI-01 returns `confirmed`, adjusted p approximately 0.000100, conservative lower bound 0.6605. This contrast is built into the known parity law and disjoint sham. It verifies the intervention pipeline and the explicit mechanism rather than a surprising neural finding.

Neural arms and scrambled-support sham abstained at the registered Laplace release gate on all 64 worlds. The compiled circuit released on all 64 and was correct on all 16,384 tests. The train-only GF(2) solver recovered rank 140 with support size six in every world, and the source oracle independently checked recovered supports against the synthetic generator's exact target mask.

## Compute accounting

Local PyTorch CPU 2.10, two torch threads; mean per-world neural fit time was **0.324 s** (flat) and **0.410 s** (tied). Mean GF(2) support-recovery time was **0.0165 s**. These timings depend on hardware and exclude some common data-generation/reporting overhead. The neural gradient steps were equal across their two arms. Sparse recovery has an explicit parity-specific algorithmic prior, so the smaller runtime must not be interpreted as proof that an equivalently general neural learner is faster. A final native-replay CI run on GitHub checks every packed per-case outcome, not just rounded table means.

## Scientific interpretation

Six-sparse parity is fully identifiable under the registered training matrices when the GF(2) rank reaches 140, but the two tested raw neural architectures fail to exploit that structure after 350 updates. A hand-specified parity-family solver recovers it, and its forward circuit has perfectly selective interventions on exactly the learned coordinates. This identifies an **inductive-bias / optimization** obstacle in the synthetic architecture experiment, with the caveat that symbolic inference and neural gradient learning have distinct hypothesis classes. It does not demonstrate that recurrence itself cannot learn parity with other curricula, longer training, feature priors or a trained mechanism-induction objective.

## Audit and reproduction

The repository archives `output/evaluation_hypergames/hg09/hg09_paired_bits.csv` with all paired 256-bit outcome masks for all four arms and their causal-selectivity endpoints, plus `hg09_worlds.json` with calibration, timing, support hashes and intervention coordinates. `scripts/verify_hg09_fsi01.py` independently reconstructs source-bound EvalMath statistics. `scripts/run_hg09_cpu.py` recomputes all worlds without private seeds. Dedicated CI pins EvalMath FSI-01 and CPU PyTorch, verifies the archive, runs focused algorithmic tests and repeats the entire 64-world neural campaign.

The two excluded smoke seeds are `2026113001` and `2026113002`, replaced before the full campaign by `2026113065` and `2026113066`. Under no circumstance should these pilot seeds be reintroduced as sealed confirmation data.
