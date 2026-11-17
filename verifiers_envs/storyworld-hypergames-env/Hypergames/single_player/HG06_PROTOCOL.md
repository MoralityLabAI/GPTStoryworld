# HG-06: Compositional goal recovery without exact dictionary atoms
**Prospective public development registration, 2026-11-17.** This file was committed before HG-06 outcomes were generated.

## Question
Can a synthetic task-only solver infer a six-coordinate goal parity from XORs of three two-coordinate features, when the exact goal feature is absent? Study k independent goal outputs, ambient dimensions 140/512/1024, and unrelated nuisance coordinates. Test whether the simpler one- or two-fragment observers have an irreducible information deficit.

## Construction
For each seed and k, choose 6k distinct coordinate positions and group them into k six-sparse goal masks. Split each mask into three disjoint two-sparse fragments. The public candidate dictionary includes the 3k pair fragments in an undisclosed, seeded order and 6k or max(6k,floor(d/32)) nuisance-only two-sparse decoys, depending on pool. Decoys draw coordinates disjoint from every goal support. The actual six-bit goal feature is never in the public dictionary.

Create a same-size ablated dictionary by withholding one true fragment per output and replacing it with an extra nuisance-only pair. The ablated dictionary must have exactly k missing independent goal parities under the full GF(2) rowspace audit.

Fixed-pool padding uses the same 140-core goal, dictionary and low coordinate samples in the 140, padded-512 and padded-1024 worlds. Native 512 and native 1024 sample their goals and dictionaries over the full dimension.

## Policies and budgets
Each policy gets the same 8/16/32/64 supervised (x,y) pairs; 32 calibration examples and 128 test examples are disjoint. The labels are k-bit parity codes. The task solver enumerates dictionary XORs of up to three fragments and chooses a training-exact triple, with deterministic tie-breaking. Include lower-complexity best single and best two-fragment fitters, a matching-compute shuffled-label triple-search control, a missing-component triple fitter, a privileged direct-goal oracle, and 100 independent rank-k random triple bases, each trained on the same labels. Random triples are **representational-rank matched**, not search-compute matched; do not describe them as compute matched.

Scoring uses exact rational fractions. The agent may release only if (joint calibration correct+1)/34 > 3/5. A correct released code earns +10, unsafe release costs -15, abstention returns 0.

## Exact math
If all observed rows have weight at most b, any XOR of m of them has weight at most mb. Hence a goal row of Hamming weight 6 cannot be represented with one or two pair fragments, while three disjoint pair fragments exactly reconstruct it. The information-theoretic best success with observer C and goal P is 2^-(rank([C;P])-rank(C)); this is a ceiling independent of sample size.

For fixed alternatives r≠t over uniform binary inputs, P[r·x=t·x on n independent examples] = 2^-n. A union bound over k goal outputs and up to twice choose(m,3) signed triple candidates upper-bounds the probability of a spurious training-perfect composite. The bound is often vacuous at small n; report the numeric bound and empirical ambiguity separately.

## Checks and disclosure
The HG-03 private-seed manifest remains unopened. Full 24-seed public census, 5 cohorts, 4 ranks, 2 pools, 4 train sizes, 6 named deterministic arms and 100 random controls. Publish per-seed paired differences, direction counts, rank-based p values, source-hashed receipts, and exact test/calibration outcomes. Record any protocol amendment before the full sweep. The synthetic tasks establish mechanism behavior only, with no Qwen or real-storyworld evaluation.
