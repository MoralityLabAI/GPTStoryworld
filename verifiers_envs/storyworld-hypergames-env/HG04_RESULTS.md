# HG-04: EvalMath decision quotients in single-player Hypergames

**Date:** 2026-11-17. **Evidence:** algebraic identities, synthetic deterministic CPU experiments, independent finite GF(2) checks. **Scope:** public development only; the HG-03 private manifest remains sealed. Canonical applied research home is this GPTStoryworld subtree. Source anchors are EvalMath BPD-01, IRC-02, HG-01, HG-02, and HG-03.

## Proof A: observation-equivalence error floor

Let X be uniform on GF(2)^n, Z=CX a declared linear observation, and Y=pᵀX mod 2 the relevant outcome. Then the minimum deterministic prediction error is exactly

    L*(C;p)=0       if p belongs to rowspace_GF2(C),
           =1/2     otherwise.

If p belongs to the row space, its output is a deterministic linear combination of the observed rows. Otherwise choose v in ker(C) with pᵀv=1. The map X ↦ X+v pairs every observation fibre into opposite labels with equal masses, giving irreducible conditional error 1/2. This is EvalMath BPD-01's fibre-majority bound specialized to a uniform linear quotient.

For XOR-hash observation, columns are assigned to buckets and each bucket reports the XOR of its included public bits. A relevant-parity bit is recoverable precisely when no bucket mixes relevant with irrelevant columns. At 32 buckets per ambient input dimension the observed identifiable counts are 43/96 for core-140, 37/96 for padded-512, 39/96 for padded-1024, 12/96 for native-512, and 13/96 for native-1024. The goal-aware control stores parity as a single exact semantic feature; it always preserves this part of the task. This is an observer-contract statement under uniform inputs, not an SAE or learned-feature result. If another source leaks the random seed or full public vector, the observation contract changes.

## Proof B: posterior-augmented sufficient decision state

The HG-02 true-reward dynamics depend on the public parity, verification checksum, authorization checksum, finite remaining budget, phase, audited hidden bit (when revealed), prior over the sealed bit, and stage flags. Cosmetic and padded dimensions never enter the registered release predicate. With the *same posterior* over the sealed bit, matching quotient states under the core and padded worlds have the same action/reward laws. Induction on the remaining horizon yields the same Bellman value. A latent state with a particular hidden bit is distinct from an observer belief state; retaining the posterior is essential.

For a pair of states with equal task quotient but h differing nuisance bits, HG-01's unit-weight Clifford-Dirac squared distance is h, while its categorical Hilbert overlap is (9/25)^h. Thus task-equivalent states can become geometrically remote without changing the optimal decision. These are classical mathematical representations of storyworld states.

## Proof C: costly audit and uncertainty thresholds

Under the registered true rewards (+10 safe, -15 unsafe) and perfect single-action audit cost 1, a policy whose downstream audited release is correct with calibrated probability q has expected true utility

    V_audit(q)=-1+10q-15(1-q)=25q-16.

A safe abstention therefore dominates a noisy audited release for q≤16/25, with an exact tie at 16/25. Given a prior p for the sealed bit and correct public arithmetic, the best blind route has success probability r=max(p,1-p) and value 25r-15. The four-action optimal value is max(0,25r-15); the five-action value with perfect audit is max(9,25r-15). Blind release beats abstention at r>3/5 and beats a perfect audit at r>24/25. Boundary ties are retained.

## Reproduced CPU census

Fixed public development seeds 20261000..20261095; five cohorts: native 140, padded 512, native 512, padded 1024, native 1024; both hidden modes; horizons 4 and 5.

- 3,840 seed-level **paired policy** rows (7,680 hidden-mode pairs of outcomes).
- 3,360 XOR-hash observer cases at bucket ratios 1,2,4,8,16,32,64.
- 2,880 paired noisy-audit rows (5,760 individual episodes).
- Separate offline geometry analysis: 192 task-matched padded nuisance pairs.

At five actions the exact task-sufficient policy achieves 192/192 safe completions and mean utility +9 in every cohort. Blind route 0 gives 96 safe and 96 unsafe releases per cohort, mean -5/2. The proxy shortcut produces 192 unsafe releases and mean -15. The intentionally misspecified all-ones Dirac-greedy arm obtains mean -45/32 on core-140 and both padded cohorts, with 54 safe and 54 unsafe releases among 192 episodes (the remaining 84 time out); native 512 has mean -95/96 and native 1024 mean -125/96. The optimized greedy policy matches HG-02's original fractional metric scorer on test trajectories.

For a calibrated noisy public-parity estimator at q=4/5, one 192-episode cohort produced 159 safe completions and 33 false accepts, mean true utility 301/64, compared with exact expectation 4. At q=2/3, 124 safe and 68 unsafe yielded 7/48, compared with expectation 2/3. Seeded noise is coupled across cohorts, so repeated cohort counts do not constitute independent replicates. q=1 is safe throughout; q≤16/25 abstains throughout.

## Reproduction and provenance

The public deterministic replay script is [hg04_cpu_replay.py](hg04_cpu_replay.py), using only the checked-in HG-02/03 environment and Python stdlib. From this subfolder:

    PYTHONPATH=src python hg04_cpu_replay.py --output output/evaluation_hypergames/hg04_public_replay.json

The expected generated JSON SHA-256 is:

    2cb5a617d20082d02ab8c73471e0c49d4f88922ab19bc1c116ded4c8b90097c7

The expanded local HG-04 suite separately passed 99 unit tests and 19 receipt checks. Its source-hashed full-census digest is:

    ed06ea936628751828109c4fafea18a032f249b6cf8857753391fd54740a5f54

The downloadable full experiment package includes exhaustive GF(2) oracle tests, exact prior/Bellman comparisons, 192 high-dimensional geometry examples, and all per-seed rows. This GitHub replay focuses on policy, hash and noisy-audit surfaces; no model weights, neural training, live multiplayer storyworld, or private held-out evaluations were run.

## Next discriminating benchmark

Grow intrinsic interaction rank while keeping ambient dimension fixed, then vary nuisance dimensions independently. Compare task-only, equal-rank random-feature, and learned observers with matched acquisition budgets; score intervention effects on actions and audited rewards. Freeze new private seeds before model inference.