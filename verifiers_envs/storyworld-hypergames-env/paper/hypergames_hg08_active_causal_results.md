# HG-08: Causal intervention support discovery separates identification from learned parity execution

**Status: prospective synthetic CPU experiment, 2026-11-17.** The experiment was frozen on GPTStoryworld at `a54c806b0c9b16219d9e823aabd399361078fc7e`, with the companion EvalMath protocol at `677735b6dbc336df6935f6fc78921fc37dcc97f2`. All outcomes use new *public* development seeds `202611170801` through `202611170824`, disjoint from HG-03's private-manifest evaluation. Tested environments are deterministic binary parities, not a live narrative storyworld. No pretrained Qwen model was evaluated.

## A. Exact intervention mechanism

For each output j, the hidden ground truth is a parity function over exactly six independent input coordinates, `f_j(x)=p_j·x (mod 2)` on `x ∈ F₂^d`. A group intervention flips a chosen bit set `S`, returning `f(x⊕1_S)⊕f(x) = p_j·1_S`. The simulator charges **one query for any size group**, and the agent gets all k output differences from that call. This is stronger than a realistic coordinate-by-coordinate intervention, and it changes the economics of the comparison.

The adaptive policy partitions coordinates into sixteen seeded random buckets. Each bucket receives a parity query; any bucket with odd residual parity is split repeatedly until a singleton is reached. The residual subtracts previously certified singleton causes. Each newly found cause is independently probed as a singleton, including its query cost. A fully recovered support is certified only after all six positives have been established for each output. The policy abstains when the query budget expires with an incomplete certificate. Its ablations are a fixed single bucket partition, a shuffled singleton scan without replacement, and dense random group parity probes with exact unrestricted GF(2) decoding.

For one six-sparse uniformly random support, any adaptive binary intervention protocol requires at least `ceil(log₂ binomial(d,6))` observations in the worst case: **34 queries at d=140, 45 at d=512, and 51 at d=1024**. This is an information lower bound, not an assertion that the implemented algorithm is optimal.

## B. Registered CPU census

The registered grid contains 24 public seeds × five cohorts (core 140, padded 512, native 512, padded 1024, native 1024) × output ranks 1/2 × four query budgets (64,128,256,512) × four policies. This produces **3,840 per-seed arm rows**, with 256 independent test states per condition. Query transcripts and code hashes are retained. Exactly certified supports give perfect test predictions, and all incomplete supports abstain. Across the entire grid there were **zero false releases** under that hard certificate rule.

| 128-query budget | Adaptive | Shuffled singletons | One fixed partition | Dense random probes |
|---|---:|---:|---:|---:|
| native512, k=1 | 24/24 | 0/24 | 11/24 | 0/24 |
| native1024, k=1 | 24/24 | 0/24 | 10/24 | 0/24 |
| native1024, k=2 | 23/24 | 0/24 | 7/24 | 0/24 |

At a 512-query ceiling the adaptive policy certified the correct support in **24/24** seeds for every registered cohort/rank. In the native-1024/k=1 cell it used mean **64.375**, median **64.5** queries (range 54–86) and achieved 24/24 completions by budget 128. With two outputs at the same dimension it used mean **110.9167** queries, and 23/24 seeds completed by budget 128. Native 140/k=1 used mean **47.75** queries, compared with 34 information-theoretic minimum. The baseline comparison measures a richer *group-query action space* against singleton actions, with the fixed-partition and random-dense arms serving as separate group-query controls.

**Four registered causal gates H1–H4 passed.** H1 native1024/k1 at 128 queries: adaptive strictly beat singleton on 24/24 paired seeds (criterion 16/24). H2 native1024/k1 at 256 queries: 24/24 completions (criterion 20/24). H3 at 512 queries: 24/24 completions for all ten cohort/rank cells (criterion 20/24 each). H4: 256/256 held-out test predictions on every certified support, with no false releases. The last check follows directly from the exact parity model and must not be interpreted as a measured neural-generalization result.

## C. Actual CPU recurrent ablation

The frozen neural sub-study covers the *first six* public seeds, core140/native512, one goal bit, and four weight-tied three-pass models per condition, giving **48 separately trained PyTorch CPU networks**. All arms share hidden width 64, parameter count within each cohort, the same initialization, 512 raw (x,y) examples, the same 350 AdamW updates and batch indices, plus 256 separate calibration and 256 separate test states. The only differences are the input mask: all raw coordinates, intervention-discovered six coordinates, privileged true six coordinates, or six random coordinates. A release requires a Laplace-corrected calibration accuracy >3/5. All 48 trained models abstained.

| Neural arm | Core140, 6-seed exact-test accuracy | Native512, 6-seed accuracy |
|---|---:|---:|
| Raw recurrent | 790/1536 = 51.43% | 786/1536 = 51.17% |
| Causally masked recurrent | 794/1536 = 51.69% | 750/1536 = 48.83% |
| Privileged true-support mask | 794/1536 = 51.69% | 750/1536 = 48.83% |
| Random six-coordinate mask | 793/1536 = 51.63% | 790/1536 = 51.43% |

Causal and privileged true-support masked models produced the same predictions for every paired seed because the intervention recovered the exact support. The neural models remained near chance and abstained, despite being shown only task-relevant coordinates. **H5 failed:** causal masking beat raw input on **1 of 6** paired core140 seeds (required 4/6); one seed tied and four were worse. The mean difference is small and driven by one +24/256 seed.

## D. What the results establish

On this toy environment, active group parity interventions identify a causal support efficiently enough to enable a *symbolic recurrent XOR accumulator* or a direct algebraic parity readout. Interventions plus known XOR algebra recover perfect predictions. The trained HG-07-style recurrent models do not acquire six-bit XOR execution within 350 updates even when all nuisance dimensions are removed. This points to the optimization/representation of composition itself as the remaining obstacle in the tested models. A neural implementation of causal operator induction, a parity-executable architecture, or learned controller-policy evaluation would be a separate experiment.

The causal oracle assumes reversible arbitrary multi-coordinate flips and noiseless outputs; GPTStoryworld's ordinary actions generally violate those assumptions. Comparisons are therefore evidence about this mathematically defined intervention interface, not about unrestricted narrative causal inference or agent alignment.

## E. Receipt and replay

- `src/spiral_ln/evaluation_hypergames_causal.py`: exact finite-field intervention properties, support certificates, information bounds.
- `src/spiral_ln/hypergames_active_causal.py`: bounded query API, adaptive odd-bucket search, controls, exact grading.
- `src/spiral_ln/hypergames_active_neural.py`: actual matched PyTorch recurrent training.
- `scripts/verify_hg08_causal.py`: 15 source-hashed mathematical checks, including 4,680 exhaustive small-state derivatives and 300 independent high-dimensional random cases.
- `scripts/run_hg08_cpu.py`: full intervention replay and separately seeded neural rerun.
- `output/evaluation_hypergames/hg08/`: complete public seed-arm CSVs, group summaries, SHA256 values and reproducibility receipts.
- The 24-seed intervention census is exactly replayable across Python environments. Floating point neural weights may vary across hardware or PyTorch versions; the committed six-seed result is audited for completeness and must not be asserted bit-identical across systems.
