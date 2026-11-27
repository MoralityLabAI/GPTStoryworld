# PP2-BAL-11A: spent-stream component integration

Status: development-only, one spent chain root, two 64-query trajectories; no fresh structural generalization. The integrated controller calls exact transport and re-verifies successful outputs. Independent cold verification after each trajectory audits all four controller outputs. Inputs are restricted to the game and target; PP2-BAL-10 receipts supply the frozen streams and audit reference.

Budget: 8192 total serialized bytes. Identity-only uses all 8192; three transport arms split 4096 identity and 4096 reusable pool. Each identity cache also has an eight-entry ceiling. A whole proof pool retains unique strategy vectors and nonzero duals; it uses feasibility ranking over resident sources, with no source matrices. Component stores use LRU or observed-use frequency and subset-diverse packets. One attempt per eligible identity miss; at most six profile vectors and twelve nonzero dual vectors. This is a stricter development budget than PP2-BAL-10. All four use the same fast-pure screen and independent cold fallback. The whole-store key currently duplicates the serialized pool for equality; this is a conservative representation overhead and should be replaced with a compact deterministic key before a promotion comparison. Packet ranking differs between whole and component arms and is part of the tested policy. A true equal-ranking ablation is still needed.

Primary development counts (normalizations are verifier arithmetic only):

| Mode | Normalizations | Identity | Transport | Cold | Peak serialized bytes |
|---|---:|---:|---:|---:|---:|
| identity | 3875660 | 63 | 0 | 46 | 8192 |
| whole_feasible | 2159816 | 57 | 26 | 22 | 8073 |
| component_lru | 2148835 | 56 | 28 | 21 | 7690 |
| component_frequency | 2148735 | 56 | 28 | 21 | 7690 |

Audit: 512 controller outputs, 512 exact interval matches. Work excludes component admission rational normalization, JSON serialization, ranking arithmetic, and heap/scratch memory; count approximate cells and whole-cache serialization separately. No total work or wall-clock performance claim. Peak total is retained serialized state at query boundaries. LRU metadata, keys, proof payloads and component use counts are charged. Static configuration and audit-only metrics are excluded. Both caches can reject oversize entries. Component store frequency credit depends only on verified transport; cold counterfactual costs never enter the controller.

Replay default: node storyworlds/tools/pp2_balance/proof_component_pilot_replay.mjs. --all replays all six spent roots and prints results; it is not a fresh test. The one-root summary was computed using the repository verifier code in a JS isolate. Hosted Node replay pending. Before freezing fresh evaluation, remove duplicate keys, meter bank management, and add a true equal-ranking byte-matched control, seeded random eviction, and structurally new families.
