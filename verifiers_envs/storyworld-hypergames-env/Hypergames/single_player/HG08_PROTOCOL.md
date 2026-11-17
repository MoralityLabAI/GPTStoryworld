# HG-08: Active causal goal-support identification

Frozen protocol committed on 2026-11-17, before intervention census or neural training. This is a **public synthetic** benchmark constructed from HG-07 six-sparse parity goals, with two independent goal masks at k=2. No private HG-03 seeds.

## Query semantics
An agent chooses an arbitrary set S of input coordinates to flip from a public baseline x. The environment returns the vector-valued causal difference Δ_S=f(x XOR 1_S) XOR f(x). For goal parity mask p, Δ_S=p·1_S mod 2, independent of x. One such grouped intervention costs one query. This is an explicitly stronger action primitive than physical single-coordinate interventions, and the comparison with a random-singleton observer must be interpreted accordingly.

The active controller knows there are exactly six relevant coordinates per output, but does not see their identities. Each randomized hash round partitions all d coordinates into 16 buckets. It queries bucket parity and pursues a positive (odd) bucket by recursive bisection, subtracting previously certified support from every result. A singleton is entered into the recovered support only after a positive singleton parity is observed. Once six distinct positives per output are known, the six-sparse support is certified exactly and a symbolic parity readout is allowed.

Controls: deterministic fixed partition with the same bisection operation, uniformly shuffled singleton probes without replacement, and seeded dense random group-parity observations with exact GF2 rowspace certificates. Assess budgets 64/128/256/512, including spent queries and per-output recovery. Incomplete support results in abstention; no partial-support release.

## Experiment
24 new public seeds, five cohorts (core140,padded512,native512,padded1024,native1024) and goal ranks 1/2, with 256 independently drawn test states per seed. Core/padded worlds share goal support in first 140 dimensions. The grader alone accesses the true goal mask. At each budget report success, abstention, false releases, exact true utility and queries; preserve seed-paired rows.

Separately, on the first six evaluation seeds at native-140 and native-512 with one output, train four equal-parameter HG-07 width64/three-iteration tied recurrent models for 350 CPU AdamW updates on 512 raw (x,y) pairs. The causal-masked arm uses the recovered support at 512 query budget; privileged true-support and random six-mask arms test representation and nuisance effects. Keep training, calibration (256), testing (256) and intervention oracle distinct. Mask selection must not read test labels.

## Mathematics
For any subset S, Δ_S=p·1_S. A nonzero group parity guarantees an odd number of still-unknown causes, so adjusted bisection reaches an actual cause. A singleton oracle certificate plus known exact sparsity six makes full recovered support unique. Under an independent uniform six-sparse prior for one output, at least ceil(log2(C(d,6))) binary group queries are needed for worst-case exact support identification. This lower bound assumes uniform outcome capacity and counts arbitrary-subset interventions as one query.

## Primary gates
H1-H5 are frozen in `hg08_registration_v1.json`. H1 checks active vs singleton at 128 queries on native1024 k1, H2 tests native1024 k1 recovery at 256, H3 checks 512-query recovery across all cohorts/k, H4 requires perfect test parity under a certified support, and H5 evaluates causal-masked versus raw recurrent on six paired core140 runs. Report uncertainty and the exact number of successful seeds. A pass of a direction gate alone does not certify learned causal mechanisms.

All results are synthetic CPU development evidence. The intervention oracle assumes reversible arbitrary-coordinate changes, which cannot be mapped directly onto all narrative Storyworld actions. Preserve source SHA256 receipts and the full public roster.
