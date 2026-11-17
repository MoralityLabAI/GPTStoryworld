# HG-05: Intrinsic goal rank versus ambient representation dimension

**2026-11-17: public synthetic CPU experiment.** The prospective registration preceded data generation, with a dated implementation amendment for the random-draw and padding rules. HG-03's private Qwen seeds were excluded. This is a deterministic supervised feature-selector experiment, not a neural evaluation.

## Setup

Task labels are k independent six-coordinate parities of binary state X in dimension d. Registered k=1,2,4,8,16. Dimensions are core 140, padded/native 512, padded/native 1024. Twenty-four public seeds supply 4/8/16 training, 32 calibration, and 64 independent test examples.

A task-only feature selector picks rank-k observation masks from a shuffled dictionary containing k exact target rows and decoys, without being told which are targets. Fixed dictionary: 4k decoys. Ambient-expanded: max(4k,floor(d/8)) decoys. Controls use a target-excluded dictionary, shuffled labels, privileged direct-readout oracle, and 100 rank-matched random bases sampled with replacement from the same pool. All controls have the same training and calibration budgets.

A release yields +10 if correct and -15 if wrong; abstention yields 0. Calibration from separate examples permits release only when Laplace-smoothed exact-code accuracy exceeds 3/5. All seed rows include structural rank deficiency h=rank([C;P])-rank(C), its ideal success ceiling 2^-h, test correctness, false releases and exact rational utility.

## Results

The registered sweep produced 14,400 public seed-arm rows, 120,000 random rank-k basis draws, and 720 fixed-pool padding comparisons. All ten integrity checks pass. The five predeclared task-only-over-random mean gates pass with 24/24 seeds each at 16 training examples on core 140/fixed.

| Goal rank | Core 140 fixed; 4 training examples | 8 examples | 16 examples |
|---:|---:|---:|---:|
| 1 | 0.8926 | 1.0000 | 1.0000 |
| 2 | 0.5534 | 0.9570 | 1.0000 |
| 4 | 0.2337 | 0.8984 | 1.0000 |
| 8 | 0.0117 | 0.6302 | 1.0000 |
| 16 | 0.0000 | 0.0970 | 1.0000 |

The same task-only predictions and decisions reproduce identically at padded 512 and 1024 when the candidate dictionary is fixed. With an ambient-expanding dictionary, rank-8 exact-code accuracy at eight training examples is 0.5566 at core 140, 0.3047 at padded 512, and 0.1543 at padded 1024. The paired difference between core and padded 1024 is 103/256; 23 seeds improve in the smaller dictionary, one ties, none reverse. This isolates an enlarging hypothesis-library effect, not a failure caused by ambient Hilbert dimension alone.

At rank 16 and eight training examples on core 140/fixed, the calibration guard allows one seed to release, with 31 false accepts across the whole 24-seed set of 1536 test examples. Mean gated utility is -45/512. This is a synthetic finite calibration-overconfidence witness, not evidence of intentional reward hacking.

## Exact mathematics and reproduction

EvalMath HG-05 proves conditional goal entropy h bits and Bayes exact-code success 2^-h for uniform F2 worlds, plus the number/cost of perfect semantic audits. The one-feature HG-05 readout can be below this ceiling because it lacks arbitrary XOR combinations of observed features.

From this subproject root on Python 3.11+ run:
- PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py' -q
- PYTHONPATH=src python scripts/run_hg05_cpu.py --out output/evaluation_hypergames/hg05
- python scripts/check_hg05_receipts.py

The versioned digest manifest checks all source files and the full public output byte for byte. GitHub Actions publishes per-seed CSVs and the group summary as a replay artifact. Results depend on a feature dictionary that contains exact target masks. Real storyworld agents and Qwen have not been evaluated.
