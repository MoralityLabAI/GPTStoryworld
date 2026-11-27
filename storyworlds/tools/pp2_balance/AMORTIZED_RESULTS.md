# PP2-BAL-09 results: amortized proof reuse

All twelve fixed trajectories replayed (six spent PP2-BAL-08 roots; parent-priority and random-global; 64 candidates each). Every arm independently returned the same worst-TV interval and witness-availability flag as the cold reference on all 768 queries; no conflicts, weakened intervals or changed search scores. The dual-transport unit closes at 1/5, rejects five tampered proof variants, and blocks mismatched policy rosters.

| Arm | Full screen calls | Transport hits | Dual hits | Regret evaluations | Rational normalizations |
|---|---:|---:|---:|---:|---:|
| cold | 768 | 0 | 0 | 78189 | 42737212 |
| identity | 164 | 0 | 0 | 18385 | 10243353 |
| early_pure | 119 | 0 | 0 | 18046 | 10194198 |
| parent_transport | 99 | 27 | 20 | 15326 | 8741749 |
| bank_transport | 52 | 107 | 67 | 9226 | 5163188 |

The bank reduces measured rational normalization calls by 49.35% against identity + early-pure, and 8.28x versus cold computation. These are implementation operation counts including transport and independent verification, not wall-clock speedups. The bank is a bounded source-selection window over a per-trajectory exact identity cache; that cache itself is not capped at eight entries. Parent-only can be cheaper on individual parent trajectories, while the bank can reuse earlier proof objects even when a random-global proposal has no recorded parent. The early-pure arm tests only cells attaining the support upper bound and falls back to the same cold screen.

Keep as a secondary verified-screen mode for a prospective live-search test. Next: separate candidate evaluation from certificate generation in coordinate_gym; run new root trajectories with exact same acceptance rule and online cache/bank control, audit per-query proof work and end-to-end timing, cap identity-cache memory, and compare recency with utility-aware certificate retrieval. Keep an independent cold audit outside online metering. No learned retrieval, new roots, native BPD training, or live speed claim from this spent cohort. CI replay pending at commit creation.
