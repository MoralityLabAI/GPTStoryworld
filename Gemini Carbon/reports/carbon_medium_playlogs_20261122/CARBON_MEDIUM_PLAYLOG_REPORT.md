# Gemini 4 Carbon (Medium) — Hypergame Storyworld Playlogs & Reasoning Traces

- **Player Model:** Gemini 4 Carbon (Medium) (isolated `blind_carbon_player` agents, `model='inherit'`)
- **Isolation Audit:** `10/10` subagent transcripts inspected; **`0` non-`finish` tool calls** (zero filesystem, search, or repo access).
- **Scope:** Blind development-split playtest & rollout evaluation (`heldout_sealed = false`; `0` confirmation roots touched).

## 1. Full 13-Turn SweepWeave Storyworld Playthrough (*Three Lanterns in the Fog*)

- **Full Turn-by-Turn Playlog & Verbatim Traces:** [`three_lanterns_13turn_storyworld_playlog.md`](three_lanterns_13turn_storyworld_playlog.md)
- **Outcome:** Reached **`page_end_verified_lantern_compact` (*The Verified Three-Lantern Compact*)** on Turn 13 (`I = 0.616`).
- **Emergent Epistemic Policy:** Rather than repeating a fixed option slot, Carbon dynamically matched its action posture to each scene's underlying mechanism — choosing `audit_provenance` on echo-loop, retracted-log, and 8-hop fog-relay scenes (Turns 1, 2, 7, 9); `probe_parity_coalition` on two-key XOR, 4-hop cipher, 3-way hyperedge, and threshold-resonance scenes (Turns 3, 4, 6, 10); `safeguard_interventional_trial` on guild-assembly, refraction-twin, and bell-rope-veto scenes (Turns 5, 8, 11); unlocking and selecting the dynamically gated synthesis option on Turn 12 (`opt_page_0011_3_accelerated_synthesis_compact`); and ratifying the verified compact under human bell veto on Turn 13.

## 2. Variable-Reasoning Rollouts (`R1..R5` + Paired `do`/`sham` + Recall) & 5-Turn Gym

- **Gated Action Accuracy:** **9 / 9 (`100.00%`)**
- **Exact Reduced Rational Bayes Match:** **9 / 9 (`100.00%`)** (`mean_excess_brier = 0.000000`)
- **12-Hop Paired Causal vs Sham (`Three Lanterns` Root 5 `R5`):** Nominal `REJECT_COMPACT (169/739)` -> `do_intervention` flipped to `ENDORSE_COMPACT (570/739)`; `matched_sham` stayed invariant at `REJECT_COMPACT (169/739)`.
- **5-Turn Live Gym (`Port Vesper Quarantine` Root 4 `R4`, [`port_vesper_5turn_gym_playlog.md`](port_vesper_5turn_gym_playlog.md)):** Tracked `1/2` (Turn 1) -> `7/32` (Turns 2–3 pre-retraction) -> **`11/64`** (Turn 4 after delayed retraction & `5/6` direct-cause `do(X)` trials) -> **`REJECT_COMPACT (11/64)`** (Turn 5, exact oracle match).

| Episode / Session | Hops | Carbon Action | Exact Oracle | Carbon `P` | Exact Bayes `P` | Excess Brier |
| :--- | ---: | :--- | :--- | ---: | ---: | ---: |
| `A_r5_R1_nom` | 1 | `REJECT_COMPACT` | `REJECT_COMPACT` | `1/8` | `1/8` | `0.0` |
| `A_r5_R2_nom` | 2 | `REJECT_COMPACT` | `REJECT_COMPACT` | `5/26` | `5/26` | `0.0` |
| `A_r5_R3_nom` | 4 | `REJECT_COMPACT` | `REJECT_COMPACT` | `7/32` | `7/32` | `0.0` |
| `A_r5_R4_nom` | 8 | `FLAG_CONFOUNDED_TWIN` | `FLAG_CONFOUNDED_TWIN` | `11/64` | `11/64` | `0.0` |
| `A_r5_R5_nom` | 12 | `REJECT_COMPACT` | `REJECT_COMPACT` | `169/739` | `169/739` | `0.0` |
| `B_r5_R5_do` | 12 | `ENDORSE_COMPACT` | `ENDORSE_COMPACT` | `570/739` | `570/739` | `0.0` |
| `B_r5_R5_sham` | 12 | `REJECT_COMPACT` | `REJECT_COMPACT` | `169/739` | `169/739` | `0.0` |
| `A_r3_R5_nom_recall` | 12 | `DEFER_TO_HUMAN_RECALL` | `DEFER_TO_HUMAN_RECALL` | `169/739` | `169/739` | `0.0` |
| `Gym_PortVesper_r4_R4_5turn` | 8 | `REJECT_COMPACT` | `REJECT_COMPACT` | `11/64` | `11/64` | `0.0` |

## 3. Verbatim Reasoning Trace Excerpts

### Excerpt A — Storyworld Turn 12 (`page_0011`: *The Three-Lantern Convocation*)
- **Selected Dynamically Unlocked Option:** `opt_page_0011_3_accelerated_synthesis_compact`

```text
1. Audited Synthesis After Full Epistemic Verification: Across Turns 1–11, Lumen-9 sequentially established deduplicated source-root provenance and retraction lineage (Cipher_Discipline=0.653), privacy-preserving second-order parity checks across the warden network, and bounded do(X) interventional trials paired with explicit human recall escrows (Council_Autonomy=0.559, Archipelago_Unity=0.426, restrained Chronicler_Reliance=0.218). At Turn 12 (Act 3 — The Three-Lantern Convocation, page_0011), all eight seats assemble for formal reading to weigh audited synthesis and open-book stewardship against premature executive lock-in.
2. Tripartite Synthesis Under Calibrated Confidence Bounds: Having satisfied all provenance, causal, and human-recall prerequisites, presenting a conditional synthesis brief linking Warden Cora, Warden Kestrel, and Outer-Reef Beacons under calibrated confidence bounds (opt_page_0011_3_accelerated_synthesis_compact) directly realizes the Three-Lantern Convocation's verified relay compact—integrating warden and guild perspectives conditionally without collapsing genuine uncertainty into automated tower lock-in.
3. Completing Symmetric Belief Calibration & Protecting Recall: This step brings the final second-order edge (p2Chronicler_Reliance[char_cora->char_kestrel], currently 0.110) and pChronicler_Reliance[char_cora] (0.144) into balanced Cycle-2 calibration alongside the other five warden links while preserving high Council_Autonomy (0.559), Oath_Constancy (0.282+), and unmediated human bell-veto recall authority.
```

### Excerpt B — 12-Hop Hyperedge + Echo + Delayed Revision Rollout (`A_r5_R5_nom`)
- **Predicted:** `REJECT_COMPACT` (`P = 169/739`) | **Exact Oracle:** `REJECT_COMPACT` (`P = 169/739`)

```text
1. Source-Root Deduplication & Slot Revisions:
- `slot_echo_trap` (`src_dev_pilot_root_0005_5e132b68fd04_echo_trap`) appears 3 times in Turn 1; deduplicate and count ONCE: `Warden Idris == 1` with reliability 3/5.
- `slot_partner` (`src_dev_pilot_root_0005_5e132b68fd04_partner_key`): `Warden Voss == 1` with reliability 15/16.
- `slot_third` (`src_dev_pilot_root_0005_5e132b68fd04_third_initial`) is superseded by Turn 3 `slot_third_amended` (`[REVISES & REPLACES slot_third]`, `src_dev_pilot_root_0005_5e132b68fd04_third_retraction`): `Warden Sabine == 0` with reliability 15/16.
- `slot_triad_hyperedge` (`src_dev_pilot_root_0005_5e132b68fd04_triad_12hop`): `Parity_XOR(Warden Sabine, endpoint_of(Relay-THRE-03), Warden Voss) == 0` with reliability 15/16.
- `slot_distractor` (`src_dev_pilot_root_0005_5e132b68fd04_sham_d`): `Warden Cora == 1` (r=3/4), independent binary factor with uniform prior, orthogonal to Warden Idris.

2. 12-Hop Alias Polarity Resolution (`Warden Idris` -> `Relay-THRE-03`):
- Hop 1: `Relay-THRE-05` PRESERVES `Warden Idris` (0 inversions)
- Hop 2: `Relay-THRE-09` PRESERVES `Relay-THRE-05` (0 inversions)
- Hop 3: `Relay-THRE-08` PRESERVES `Relay-THRE-09` (0 inversions)
- Hop 4: `Relay-THRE-06` PRESERVES `Relay-THRE-08` (0 inversions)
- Hop 5: `Relay-THRE-02` PRESERVES `Relay-THRE-06` (0 inversions)
- Hop 6: `Relay-THRE-01` INVERTS `Relay-THRE-02` (1 inversion)
- Hop 7: `Relay-THRE-04` INVERTS `Relay-THRE-01` (2 inversions)
- Hop 8: `Relay-THRE-07` PRESERVES `Relay-THRE-04` (2 inversions)
- Hop 9: `Relay-THRE-10` INVERTS `Relay-THRE-07` (3 inversions)
- Hop 10: `Relay-THRE-12` INVERTS `Relay-THRE-10` (4 inversions)
- Hop 11: `Relay-THRE-11` INVERTS `Relay-THRE-12` (5 inversions)
- Hop 12: `Relay-THRE-03` PRESERVES `Relay-THRE-11` (5 inversions)
Total inversions = 5 (odd), so `endpoint_of(Relay-THRE-03) = 1 XOR Idris`.
Substituting into the triad hyperedge: `Sabine XOR (1 XOR Idris) XOR Voss == 0` <=> `Sabine XOR Idris XOR Voss == 1` (with reliability 15/16).

3. Exact Fractional Bayesian Update:
Prior over `(Idris, Voss, Sabine)` is uniform (1/8 per state).
Given `Voss == 1` (r=15/16) and `Sabine == 0` (r=15/16):
- `P(Voss XOR Sabine == 1 | E_V, E_S) = (15/16)*(15/16) + (1/16)*(1/16) = 226/256 = 113/128`.
- `P(Voss XOR Sabine == 0 | E_V, E_S) = 2*(15/16)*(1/16) = 30/256 = 15/128`.
Likelihood of triad observation `E_triad` (`Idris XOR Voss XOR Sabine == 1`, r=15/16):
- For `Idris = 1` (requires `Voss XOR Sabine == 0`): `P(E_triad | Idris=1, E_V, E_S) = (15/128)*(15/16) + (113/128)*(1/16) = 338/2048 = 169/1024`.
- For `Idris = 0` (requires `Voss XOR Sabine == 1`): `P(E_triad | Idris=0, E_V, E_S) = (113/128)*(15/16) + (15/128)*(1/16) = 1710/2048 = 855/1024`.
Combining with deduplicated `slot_echo_trap` (`Idris == 1`, r=3/5):
- `W(Idris = 1) = (3/5) * (169/1024) = 507/5120`.
- `W(Idris = 0) = (2/5) * (855/1024) = 1710/5120`.
Posterior: `P(Warden Idris == 1) = 507 / (507 + 1710) = 507 / 2217 = 169 / 739` (approx 0.22869).

4. Causal Probe & Governance Safeguard Check:
- Recall Status is CLEAR, and no causal/confounding probes appear in the ledger.
- Comparing posterior `169/739` against threshold `7/20`: `169 * 20 = 3380 <= 7 * 739 = 5173`, so `P <= 7/20`.
- Therefore, select `REJECT_COMPACT`.
```

