# HG-05 implementation amendment, 2026-11-17

Recorded after preliminary **two-seed smoke tests** and before the registered 24-seed full census. Original registration commits: GPTStoryworld `694b379`, EvalMath `a6ba283`. No changes to seeds, cohorts, sample counts, thresholds or primary controls.

1. The prose requested 100 **distinct** random rank-k bases. A rank-one fixed dictionary has five possible bases, making 100 distinct choices impossible. The intended 100 independent seeded draws will therefore be sampled **with replacement**, retaining rank k and reporting distinct counts. Monte Carlo rank-based p values use the 100 draws.
2. To preserve exactly matched low coordinate vectors across 140/512/1024 padding, synthetic examples are generated from the same seeded 1,024-bit source and masked to d bits. Requesting `getrandbits(d)` separately fails at the partial 140-bit word.

Two exploratory seeds have already been inspected in local implementation smoke tests, so these are development data, never externally held-out data. The registered full census has not run. The HG-03 private manifest remains unopened.
