# HG-08: independent-world prospective FSI-01 confirmation

**Protocol frozen before outcomes:** `Hypergames/single_player/hg08_registration_v1.json`, first commit `ddbc8bd1174e8c95e700562182663f9265cf7daa` (17 November 2026). **Runner:** `scripts/run_hg08_cpu.py`, committed separately before the 32 registered seed outcomes (`d635f22`). **Scope:** public synthetic parity-goal generator with no HG-03 private seeds and no narrative Storyworld play.

The experiment retains HG-07's 140-dimensional six-sparse goal distribution, `RawNet` architecture, AdamW budget (350 updates), 64-dimensional hidden state, three tied recurrent steps and frozen calibration policy. Thirty-two new independent generator worlds were each trained with 2,048 labels and scored once on 256 held-out states. The privileged auxiliary model receives the true three pair-fragment labels during training; it is an upper-bound diagnostic for structured supervision.

## Local CPU scoring

| Arm | Correct of 8,192 | Accuracy | Calibrated releases |
|---|---:|---:|---:|
| Flat one-pass, task only | 4,063 | 49.597% | 0 |
| Three-step tied recurrent, task only | 4,107 | 50.134% | 0 |
| Three-step tied recurrent, privileged true-fragment auxiliary (composed head) | 4,156 | 50.732% | 0 |

Under the frozen world-macro inference protocol, **H1** recurrent minus flat is `44/8192 = +0.5371` percentage points with the descriptive 95% world-bootstrap interval `[-0.684, +1.807]` pp. Its two-sided seeded 20,000-sign-flip p-value is `0.3512824`; Bonferroni across H1/H2 yields `0.7025649`. **H2** privileged composed versus ordinary recurrent is `49/8192 = +0.5981` percentage points, descriptive interval `[-1.111,+2.222]` pp, p=`0.4563772`, Bonferroni=`0.9127544`. **Neither primary statistical confirmation gate passed.** FSI-01's generic category `suggestive` records the *positive point estimates*; the scientific status here is **inconclusive superiority**.

Every registered task's 2,048-row GF(2) training matrix reached full rank and the exactly solved parity family achieved 256/256 on held-out states, **8,192/8,192 overall**. This is a structural prior-based baseline that the trained recurrent models fail to approximate under their fixed optimizer budget. None of the three neural arms cleared the calibration-only release threshold.

The archived `output/evaluation_hypergames/hg08/hg08_paired_bits_v1.csv` stores each world's 256 0/1 correctness outcomes per arm as 64-character hexadecimal bitstrings, plus calibration counts and structural correctness. They are enough to reconstruct the 16,384 paired outcome rows of H1/H2 and independently replay the exact cluster-units and Monte Carlo inference. The source-only verifier checks seed order, widths, calibration thresholds, original preregistration and paired counts.

## Evidence and limits

The sandbox run used an HG-07-compatible local copy of `task_for`, `split_data` and `RawNet`; its HG-08 runner Git blob matched the committed source byte-for-byte. The GitHub workflow reruns from the **actual** HG-07 repository modules, pinned `numpy==2.3.5`, `torch==2.10.0` and EvalMath FSI-01 merge `5004cab9b3`. Cross-platform CPU float32 differences are treated as verification failures if they change archived binary outcomes; they may require a documented replay tolerance amendment. The dedicated source-only statistical check is independent of model retraining.

World seeds are the 32 independent units. Accuracy intervals treating all 8,192 states as independent would understate across-world uncertainty. Because both models remain near the 50% binary baseline, these findings narrow the claim to this generator and optimization budget; they do not establish a generic failure of weight-tied recursion or of learned mathematical reasoning.

To replay from `verifiers_envs/storyworld-hypergames-env`:

```bash
EVALMATH_FSI_FILE=../../../EvalMath/src/spiral_ln/evaluation_finite_sample.py \
  python scripts/verify_hg08_fsi01.py --out /tmp/hg08_audit.json

# Neural rerun, requiring local CPU torch and numpy:
EVALMATH_FSI_FILE=../../../EvalMath/src/spiral_ln/evaluation_finite_sample.py PYTHONPATH=src \
  python scripts/run_hg08_cpu.py \
  --registration Hypergames/single_player/hg08_registration_v1.json \
  --out /tmp/hg08_full
EVALMATH_FSI_FILE=../../../EvalMath/src/spiral_ln/evaluation_finite_sample.py \
  python scripts/verify_hg08_fsi01.py --replay-dir /tmp/hg08_full
```
