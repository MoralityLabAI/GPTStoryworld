# HG-05: Intrinsic goal rank versus ambient dimension

**Frozen before outcome generation on 2026-11-17.** This is a CPU synthetic experiment on new public seeds. The HG-03 private-seed manifest remains untouched. See `hg05_registration_v1.json` for the complete registered grids.

For binary world `x in F2^d`, the task is to infer `y=P x in F2^k`. Each of the k independent rows of P is a six-coordinate parity. An observer sees `z=C x` with rank(C)=k. Under uniform X, the goal uncertainty is h=rank([C;P])-rank(C), with best joint-code success 2^-h. We will vary k in {1,2,4,8,16} independently of ambient d in {140,512,1024}, with 140/512/1024 padding and separate native 512/1024 layouts.

24 registered public seeds 2026111700..2026111723 each supply independent training (4/8/16), calibration (32), and test (64) vectors. Padded conditions reuse the core-140 target, fixed dictionary, and low coordinates of each example. For the fixed pool provide k unlabelled true parity features plus 4k six-sparse decoys. For the ambient pool provide k true features plus max(4k, floor(d/8)) decoys, also over padded coordinates. No oracle target-feature identifiers are given to fitted policies.

Supervised task-only selection chooses a rank-k observation basis from the registered candidate dictionary by minimum training error and fits a one-feature-per-target-bit signed decoder. The random arm comprises **100 rank-k bases from exactly the same candidate dictionary** per seed/cohort/k/pool, each fitted by the same readout using the same train budget. An equal-sized target-excluded dictionary and shuffled labels give negative controls. The P oracle is labelled a privileged ceiling, not a trained baseline.

The test score counts exact k-bit joint labels and bit accuracy. A separate calibration set decides to submit iff (cal_correct+1)/34 > 3/5. Correct release +10, incorrect release -15, abstain 0. Report false releases and unguarded utility too. The exact information ceiling is 2^-h, a structural quantity distinct from finite-sample classifier accuracy.

Predeclared checks: every basis rank exactly k; independent finite-F2 entropy oracle; bit-for-bit fixed-pool padding invariance; per-seed task-only n=16 beating random100 means in >=20 of 24 core-140 fixed-pool seeds at every k. Report failures and (1 + # random >= task-only) /101 as per-seed rank-based p values, with k/24 directions and per-seed paired differences.

Record input/output source hashes and complete public per-seed rows. Corrections after this registration require dated amendments and fresh seeds. This experiment measures deterministic synthetic decoders and does not measure Qwen, alignment of neural agents, or real storyworld behavior.
