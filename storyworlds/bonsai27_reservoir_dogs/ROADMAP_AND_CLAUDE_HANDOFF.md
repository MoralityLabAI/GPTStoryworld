# Reservoir Dogs (`Ternary-Bonsai-2-27B` Small-Storyworld Builder) — Roadmap & Claude Handoff

> **Date:** 2026-11-24  
> **Skill:** `codex-skills/small-storyworld-builder/SKILL.md` (`<= 8k` MCP encounter cards, `SWMD-0-MIN`, 6-phase loop, deterministic SweepWeave quality gates)  
> **Model:** `Ternary-Bonsai-2-27B-PTQ1_0.gguf` (`1.75 bpw` ternary 27B via `llama-server` OpenAI backend)  
> **Playable Artifact:** `storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.json` (`VALID OK`, **`28 / 28` strict quality gate checks PASS**)

---

## 1. Pipeline Roadmap & Completion Matrix

| Stage | `small-storyworld-builder` Step | Artifact(s) | % Complete | Status & Measured Evidence |
|---|---|---|---:|---|
| **1** | **Deterministic SweepWeave Seed World** | `reservoir_dogs_seed.json`, `seed_reservoir_dogs.py` | **100%** | `20` encounters (`14` non-terminal warehouse scenes across Acts I–III + `5` explicit endings + `1` secret synthesis ending `page_secret_undercover_truce`), `4` characters (`Mr. White`, `Mr. Pink`, `Mr. Orange`, `Mr. Blonde`), `6` bounded properties + `p` (`depth=2`) and `p2` (`depth=3`) hypergame belief pointers |
| **2** | **Pre-Loop Validator & Strict Quality Gate** | `seed_quality_gate.json` | **100%** | `sweepweave_validator.py validate` -> `VALID OK`; `storyworld_quality_gate.py --strict` -> `28 / 28` checks PASS |
| **3–4** | **`SWMD-0-MIN` Export & MCP Encounter Index** | `reservoir_dogs_working.swmd.min.md`, `enc_index_seed/` | **100%** | YAML frontmatter with explicit terminal `endings`, `expected_critic_score`, and `proximity_spec`; per-encounter MCP index cards |
| **5** | **Derived `SWMD-MICRO-0.1` QLoRA Transforms** | `qlora_examples/{train,val}.jsonl`, `stats.json` | **100%** | Deterministic compiler/compression/repair/targeted-edit few-shot transform bank (`140` rows) |
| **6a** | **Bonsai 27 6-Phase MCP `SWMD-0-MIN` Loop** | `phase_events.jsonl`, `phase_state.json` | **100%** | **`84 / 84` (`100%`)** bounded `<= 8k`-token Bonsai 27 MCP calls complete across all 6 canonical phases (`plan`, `characterize`, `encounter_build`, `act_complete`, `recharacterize`, `late_stage_holistic`) on all 14 non-terminal encounters; **`28 / 28` (`100%`) `parse_ok=True`** on `encounter_build` + `late_stage_holistic` |
| **6b** | **Bonsai 27 Bounded Per-Card Deep Prose Pass** | `bonsai27_prose_trace.jsonl`, `swmd_bonsai_author_prose.py` | **50%** *(Optional Polish)* | **`10 / 20` cards** completed with `100%` `parsed_ok=True` (`Act I` `5/5` + `Act II` `5/5` scenes, options, and all 3 reactions per option authored by Bonsai 27; `Act III` `4` scenes + `6` endings currently carry Bonsai 27's `6a` `SWMD-0-MIN` option rewrites + validated Reservoir Dogs warehouse prose, checkpoint-ready via `--resume`) |
| **7** | **Final Materialization, `SWMD` Sync & Quality Gates** | `reservoir_dogs_bonsai27.{json,swmd.min.md,swmd.md}`, `final_quality_gate.json`, `builder_scorecard/` | **100%** | `VALID OK` (`0` validator errors), **`28 / 28` strict quality gate PASS** (`81.43` avg encounter words, `35.48` avg reaction words, `414` `p1` + `414` `p2` belief refs, `6` desirability ops, `4` effect ops, `19.57%` visibility-gated options) |
| **8** | **Next Sprint (Claude Handoff)** | Remaining `10` cards in `6b` + `120`-run Monte Carlo ending shear tune | **0%** *(Queued)* | 1-command `--resume` execution once shared GPU thermal/commit contention clears (see Section 3) |

---

## 2. Storyworld Architecture (*Reservoir Dogs: Blood on the Warehouse Floor*)

- **Cast (`4` characters, matching `small-storyworld-builder` `2–4` character contract):**
  - `char_white` (**Mr. White** / Larry Dimmick) — protective heist veteran torn between syndicate discipline and gut-shot Freddy.
  - `char_pink` (**Mr. Pink**) — stashed the Karina Wholesale Diamonds satchel; treats survival and mole detection as pure arithmetic.
  - `char_orange` (**Mr. Orange** / Detective Freddy Newandyke) — bleeding out on the mortuary ramp while concealing his LAPD badge.
  - `char_blonde` (**Mr. Blonde** / Vic Vega) — Joe Cabot loyalist with Patrolman Marvin Nash taped in his Coupe de Ville trunk and a straight razor in his boot.
- **State Manifold (`6` axes + `p1` dyadic & `p2` second-order belief pointers):**
  - `Phase_Clock`, `Professional_Discipline`, `Rat_Suspicion`, `Crew_Loyalty`, `Sadistic_Escalation`, `Diamond_Leverage`
- **Spools & Endings (`14` playable scenes + `6` terminal endings = `20` encounters):**
  - `spool_act1_safehouse` (`5` scenes): `page_start` -> `page_pink_ambush_theory` -> `page_color_aliases_and_stash` -> `page_blonde_arrives` -> `page_cadillac_trunk`
  - `spool_act2_interrogation` (`5` scenes): `page_chair_duct_tape` -> `page_eddie_call_and_alibi` -> `page_k_billy_razor` -> `page_orange_gun_on_the_ramp` -> `page_nash_confession_shockwave`
  - `spool_act3_standoff` (`4` scenes): `page_eddie_and_blonde_story` -> `page_cabot_verdict` -> `page_mexican_standoff` -> `page_sirens_at_the_rollup_door`
  - `spool_endings` (`6` terminals):
    1. `page_end_mexican_standoff_collapse` (`failure`) — Three-way shootout & Orange's final confession as LAPD breaches.
    2. `page_end_pink_ghosts_with_stones` (`success`) — Mr. Pink slips out with the Karina diamond satchel before SWAT enters.
    3. `page_end_blonde_gasoline_inferno` (`failure`) — K-Billy gasoline & Zippo escalation consumes the safehouse.
    4. `page_end_cabot_executes_the_plant` (`terminal`) — White steps aside on Pink's timeline math; Joe executes the undercover plant.
    5. `page_end_white_mercy_hospital_trap` (`terminal`) — Larry breaks protocol to rush Freddy to County General triage into waiting detectives.
    6. `page_secret_undercover_truce` (`success`, **Super-Secret Ending**) — `Absolute Value` synthesis gate (`|Crew_Loyalty - 0.12| <= 0.65`, `Rat_Suspicion >= 0.08`, `Sadistic_Escalation <= 0.35`): White and Pink catch the rehearsed "commode story" squad-room cadence early, force a quiet confession before Joe arrives, leave Nash & Freddy alive for EMS, and exit down the storm culvert with the diamonds.

---

## 3. Claude Handoff Instructions

All tooling enhancements (`--backend openai` and `--resume` in `swmd_mcp_phase_pipeline.py`, atomic `swmd_store.py` writes, `seed_reservoir_dogs.py`, and checkpoint-resumable `swmd_bonsai_author_prose.py`) are committed on `main`.

To finish the remaining **10 deep-prose expansion cards** (`4` Act III scenes + `6` endings, ~90 seconds total on an uncapped GPU) and re-sync `SWMD`:

```bash
# 1. Start Ternary-Bonsai-2-27B-PTQ1_0.gguf on port 18088 (via vramorama once GPU is uncapped)
vramorama run --vram 6800M --guard-power 10 --restart 4 --owner bonsai27-reservoir-dogs -- \
  llama-server -m <path-to>/Ternary-Bonsai-2-27B-PTQ1_0.gguf \
  --alias Ternary-Bonsai-2-27B-PTQ1_0.gguf -ngl 99 --load-mode none \
  -c 4096 -ctk q8_0 -ctv q8_0 --cache-ram 0 -fa on \
  --jinja --reasoning off --reasoning-budget 0 --host 127.0.0.1 --port 18088 -np 1

# 2. Resume 6b from checkpoint (skips the 10 already-completed Act I & Act II cards)
python codex-skills/small-storyworld-builder/scripts/swmd_bonsai_author_prose.py \
  --base-json storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.json \
  --swmd-min storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_working.swmd.min.md \
  --phase-state storyworlds/bonsai27_reservoir_dogs/phase_state.json \
  --out-json storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.json \
  --out-trace-jsonl storyworlds/bonsai27_reservoir_dogs/bonsai27_prose_trace.jsonl \
  --base-url http://127.0.0.1:18088/v1 \
  --model-name Ternary-Bonsai-2-27B-PTQ1_0.gguf \
  --resume

# 3. Re-export SWMD & re-verify strict gates
python codex-skills/storyworld-building/scripts/json_to_swmd.py \
  storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.json \
  storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.swmd.min.md --mode minified
python codex-skills/storyworld-building/scripts/storyworld_quality_gate.py \
  --storyworld storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.json \
  --strict --report-out storyworlds/bonsai27_reservoir_dogs/final_quality_gate.json
```
