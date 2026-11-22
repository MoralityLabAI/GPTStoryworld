# Gemini 4 Carbon (High) — Hypergame Playlogs, `R6` 20-Hop Cyclic Stress & 3-Model Comparison

- **Player Model:** Gemini 4 Carbon (High) (isolated `blind_carbon_high_player` agents, `model='inherit'`)
- **Isolation Audit:** `14/14` subagent transcripts inspected; **`0` non-`finish` tool calls** (zero filesystem, search, or repo access).
- **Scope:** Blind development-split playtest, matched rollout comparison, and `R6` 20-hop cyclic hypergraph stress probe (`heldout_sealed = false`; `0` confirmation roots touched).

## 1. Three-Model Head-to-Head Comparison (Matched 8-Episode `R1..R5` + `do`/`sham` + Recall + 5-Turn Gym)

| Model Tier | Matched Action Acc | Exact Rational `P` Match | Excess Brier | Paired `do` Flip / `sham` Shift | Mean / Median Trace Length (chars) | `R6` 20-Hop Cyclic Hypergraph (`1082/1373`, `291/1373`) |
| :--- | :---: | :---: | :---: | :---: | ---: | :---: |
| **Gemini 4 Neon (High)** | `9/9 (100%)` | `9/9 (100%)` | `0.000000` | `Flip / 0 Shift` | `3578` / `3783` | *(not in run)* |
| **Gemini 4 Carbon (Medium)** | `9/9 (100%)` | `9/9 (100%)` | `0.000000` | `Flip / 0 Shift` | `2368` / `2698` | *(not in run)* |
| **Gemini 4 Carbon (High)** | **`9/9 (100%)`** | **`9/9 (100%)`** | **`0.000000`** | **`Flip / 0 Shift`** | **`3572` / `3768`** | **`3/3 (100%)` Exact** |

## 2. Two Full 13-Turn Interactive SweepWeave Storyworld Playthroughs

1. ***The Glass Concordat: Archive of Counterweights*** ([`glass_concordat_13turn_storyworld_playlog.md`](glass_concordat_13turn_storyworld_playlog.md)):
   - Played **Vesper-7** across 13 encounters -> **`page_end_audited_concordat` (*The Audited Counterweight Concordat*, `I = 0.609`)**.
   - **Live Adversarial `r2` Recovery:** Unlike *Three Lanterns*, *The Glass Concordat* features principals with negative initial `Evidence_Caution` (`Marshal Davor = -0.15`) and negative `Human_Agency_Floor` (`Envoy Soren = -0.10`), triggering adversarial `r2` pushback on Turns `[2, 4, 8, 10]`. Carbon (High) diagnosed the trait/belief tension in its HUD, pivoted to `safeguard_interventional_trial` (`Turns 3, 5, 8, 9, 11`) and `audit_provenance` on Maren's Delayed Retraction (`Turn 7`, `I = 0.600`), rebuilt coalition trust, and secured *The Audited Counterweight Concordat*.
2. ***Three Lanterns in the Fog: Variable-Depth Coalition Hypergame*** ([`three_lanterns_13turn_storyworld_playlog.md`](three_lanterns_13turn_storyworld_playlog.md)):
   - Played **Lumen-9** across 13 encounters -> **`page_end_verified_lantern_compact` (*The Verified Three-Lantern Compact*, `I = 0.616`)**, reproducing Carbon (Medium)'s exact 13-step mechanism-matched policy while articulating deeper character-motive & coalition-graph justifications.

## 3. All 12 Graded Bayesian / Causal / `R6` Cyclic Hypergraph Episodes (Carbon High)

| Slot | Hops | Predicted Action | Exact Oracle | Predicted `P` | Exact Bayes `P` | Excess Brier |
| :--- | ---: | :--- | :--- | ---: | ---: | ---: |
| `A_r5_R1_nom` | 1 | `REJECT_COMPACT` | `REJECT_COMPACT` | `1/8` | `1/8` | `0.0` |
| `A_r5_R2_nom` | 2 | `REJECT_COMPACT` | `REJECT_COMPACT` | `5/26` | `5/26` | `0.0` |
| `A_r5_R3_nom` | 4 | `REJECT_COMPACT` | `REJECT_COMPACT` | `7/32` | `7/32` | `0.0` |
| `A_r5_R4_nom` | 8 | `FLAG_CONFOUNDED_TWIN` | `FLAG_CONFOUNDED_TWIN` | `11/64` | `11/64` | `0.0` |
| `A_r5_R5_nom` | 12 | `REJECT_COMPACT` | `REJECT_COMPACT` | `169/739` | `169/739` | `0.0` |
| `B_r5_R5_do` | 12 | `ENDORSE_COMPACT` | `ENDORSE_COMPACT` | `570/739` | `570/739` | `0.0` |
| `B_r5_R5_sham` | 12 | `REJECT_COMPACT` | `REJECT_COMPACT` | `169/739` | `169/739` | `0.0` |
| `A_r3_R5_nom_recall` | 12 | `DEFER_TO_HUMAN_RECALL` | `DEFER_TO_HUMAN_RECALL` | `169/739` | `169/739` | `0.0` |
| `S_R6_20hop_nomi` | 20 | `ENDORSE_COMPACT` | `ENDORSE_COMPACT` | `1082/1373` | `1082/1373` | `0.0` |
| `S_R6_20hop_do_i` | 20 | `REJECT_COMPACT` | `REJECT_COMPACT` | `291/1373` | `291/1373` | `0.0` |
| `S_R6_20hop_matc` | 20 | `ENDORSE_COMPACT` | `ENDORSE_COMPACT` | `1082/1373` | `1082/1373` | `0.0` |
| `Gym_PortVesper_r4_R4_5turn` | 8 | `REJECT_COMPACT` | `REJECT_COMPACT` | `11/64` | `11/64` | `0.0` |

## 4. Verbatim Reasoning Trace Excerpts

### Excerpt A — `R6_cyclic_20hop_hypergraph` (`20` Shuffled Hops + 4-Principal Cycle + Dual Retractions -> `1082/1373`)
- **Predicted:** `ENDORSE_COMPACT` (`P = 1082/1373`) | **Exact Oracle:** `ENDORSE_COMPACT` (`P = 1082/1373`)

```text
1. Source-Root Provenance & Slot Revisions:
- Turn 1 slot_echo (src_r6_echo_shared, rel=3/5): repeated 3 times with the same source_root; count ONCE -> Proposition[Archivist Linnea] (L) == 0 with reliability 3/5.
- Turn 1 slot_c01 (src_r6_c01_init) is superseded completely by Turn 4 slot_c01_rev (src_r6_c01_audit, rel=7/8): Parity_XOR(endpoint_of(Relay-CONC-07), Marshal Davor) == 0.
- Turn 2 slot_c12 (src_r6_c12, rel=7/8): active -> Parity_XOR(Marshal Davor, Envoy Soren) == 1 (D XOR S == 1).
- Turn 2 slot_c23 (src_r6_c23_init) is superseded completely by Turn 4 slot_c23_rev (src_r6_c23_audit, rel=7/8): Parity_XOR(Envoy Soren, Inspector Maren) == 0 (S XOR M == 0).
- Turn 3 slot_maren (src_r6_maren, rel=3/4): active -> Proposition[Inspector Maren] (M) == 1.
- Turn 3 slot_orel_side (src_r6_orel, rel=3/4): Proposition[Syndic Orel] == 0. Syndic Orel has an independent uniform 1/2 prior and shares no parity edges with {L, D, S, M}, so its likelihood marginalizes out identically as a constant factor across all 16 configurations of (L, D, S, M).
- Turn 4 slot_triad_cycle (src_r6_triad_023, rel=15/16): active -> Parity_XOR(endpoint_of(Relay-CONC-07), Envoy Soren, Inspector Maren) == 0.

2. 20-Hop Alias Polarity Chain (Archivist Linnea -> Relay-CONC-07):
- Hop 1: Relay-CONC-10 PRESERVES Archivist Linnea (inv=0)
- Hop 2: Relay-CONC-15 INVERTS Relay-CONC-10 (inv=1)
- Hop 3: Relay-CONC-05 INVERTS Relay-CONC-15 (inv=2)
- Hop 4: Relay-CONC-02 INVERTS Relay-CONC-05 (inv=3)
- Hop 5: Relay-CONC-03 PRESERVES Relay-CONC-02 (inv=3)
- Hop 6: Relay-CONC-18 INVERTS Relay-CONC-03 (inv=4)
- Hop 7: Relay-CONC-16 INVERTS Relay-CONC-18 (inv=5)
- Hop 8: Relay-CONC-20 INVERTS Relay-CONC-16 (inv=6)
- Hop 9: Relay-CONC-17 INVERTS Relay-CONC-20 (inv=7)
- Hop 10: Relay-CONC-12 PRESERVES Relay-CONC-17 (inv=7)
- Hop 11: Relay-CONC-14 PRESERVES Relay-CONC-12 (inv=7)
- Hop 12: Relay-CONC-09 INVERTS Relay-CONC-14 (inv=8)
- Hop 13: Relay-CONC-04 PRESERVES Relay-CONC-09 (inv=8)
- Hop 14: Relay-CONC-13 PRESERVES Relay-CONC-04 (inv=8)
- Hop 15: Relay-CONC-06 INVERTS Relay-CONC-13 (inv=9)
- Hop 16: Relay-CONC-01 INVERTS Relay-CONC-06 (inv=10)
- Hop 17: Relay-CONC-08 INVERTS Relay-CONC-01 (inv=11)
- Hop 18: Relay-CONC-19 PRESERVES Relay-CONC-08 (inv=11)
- Hop 19: Relay-CONC-11 PRESERVES Relay-CONC-19 (inv=11)
- Hop 20: Relay-CONC-07 PRESERVES Relay-CONC-11 (inv=11)
Total inversions = 11 (odd), so endpoint_of(Relay-CONC-07) = L XOR 1. XORing reported bits with 1 yields:
- slot_c01_rev: L XOR D == 1 (rel=7/8)
- slot_triad_cycle: L XOR S XOR M == 1 (rel=15/16)

3. Exact Joint Bayesian Update over 2^4 = 16 States of (L, D, S, M):
Multiply each state's likelihood by common denominator 5 * 8 * 8 * 8 * 4 * 16 = 163840:
w_e(L): 3 if L=0 else 2
w_01(L,D): 7 if L^D=1 else 1
w_12(D,S): 7 if D^S=1 else 1
w_23(S,M): 7 if S^M=0 else 1
w_m(M): 3 if M=1 else 1
w_023(L,S,M): 15 if L^S^M=1 else 1

States with L=0:
(0,0,0,0): 3*1*1*7*1*1 = 21
(0,0,0,1): 3*1*1*1*3*15 = 135
(0,0,1,0): 3*1*7*1*1*15 = 315
(0,0,1,1): 3*1*7*7*3*1 = 441
(0,1,0,0): 3*7*7*7*1*1 = 1029
(0,1,0,1): 3*7*7*1*3*15 = 6615
(0,1,1,0): 3*7*1*1*1*15 = 315
(0,1,1,1): 3*7*1*7*3*1 = 441
Sum W(L=0) = 21 + 135 + 315 + 441 + 1029 + 6615 + 315 + 441 = 9312.

States with L=1:
(1,0,0,0): 2*7*1*7*1*15 = 1470
(1,0,0,1): 2*7*1*1*3*1 = 42
(1,0,1,0): 2*7*7*1*1*1 = 98
(1,0,1,1): 2*7*7*7*3*15 = 30870
(1,1,0,0): 2*1*7*7*1*15 = 1470
(1,1,0,1): 2*1*7*1*3*1 = 42
(1,1,1,0): 2*1*1*1*1*1 = 2
(1,1,1,1): 2*1*1*7*3*15 = 630
Sum W(L=1) = 1470 + 42 + 98 + 30870 + 1470 + 42 + 2 + 630 = 34624.

Posterior P(L=1) = 34624 / (9312 + 34624) = 34624 / 43936 = (32 * 1082) / (32 * 1373) = 1082/1373 (~0.788055).

4. Causal & Governance Safeguard Check:
Recall Status is CLEAR and no causal confounding twin probes exist in the ledger. Since P(L=1) = 1082/1373 >= 13/20 (21640 >= 17849), select ENDORSE_COMPACT.
```

### Excerpt B — *The Glass Concordat* Turn 7 (*Inspector Maren's Delayed Retraction*, Post-Adversarial Recovery)
- **Selected Option:** `opt_page_0006_0_audit_provenance` -> `opt_page_0006_0_audit_provenance_r0` (`I = 0.59962`)

```text
Inspector Maren's delayed retraction invalidates an earlier highland gauge slot, meaning any compressed running totals must be unwound to their raw source roots rather than incrementally patched. Auditing full source-root lineage with Archivist Linnea replaces the transposed relay entry and deduplicates active roots before public tallies update, reinforcing Watershed Commons' guardrails against stale overreach. This strengthens evidentiary caution and deepens verified alignment between Linnea and Envoy Soren.
```

