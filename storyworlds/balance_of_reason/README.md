# Balance of Reason: The Red Mihna

**Alternate-history geopolitical simulation · 2034–2041 · AI world war, international development and internal fitnas**

An extraordinary Chinese Communist Party congress adopts Muʿtazilī theology and declares an ambition to lead the Ummah. The player is fictional Secretary **Lin Wenqi**, responsible for defending the new Party doctrine while preserving the freedom of other Muslims to dispute it. A vast system of development finance and Chinese infrastructure attracts governments whose populations may reject religious leadership from Beijing. When AI-generated diplomatic evidence triggers military escalation, the crisis becomes a global war that competing human and machine institutions struggle to control.

The central question is whether a political power can claim an Islamic rationalist mandate while guaranteeing the right to reject its conclusions. Every event is fictional and the model's numbers are authored game mechanics.

## Playing the campaign

From this folder:

```sh
python -m http.server 8000
```

Open **http://localhost:8000** in a modern browser. The standalone app imports `engine.mjs` and reads `source_cards.json`. Select a policy with the mouse or keys **1**, **2**, or **3**. The sidebar displays all 16 bounded state metrics and their consequences. **Analyst mode** reveals the authored immediate deltas; dependent knock-on effects, such as coercion increasing fitna or failed AI control intensifying war, still matter. **Export decision trace** saves the complete history, suitable for agent evaluations or narrative analysis.

The native Sweepweave world can be played with the repository-root `storyworld_reader.html`, using its file picker to load the generated `storyworlds/balance_of_reason/storyworld.json`.

## Contents

| File | Purpose |
| --- | --- |
| `source_cards.json` | Canonical authored text and mechanics: eight acts, 56 policy encounters, four pairs of war/peace branches, fifteen endings |
| `engine.mjs` | Deterministic game engine for diplomacy, AI escalation, peace and internal conflict |
| `index.html` | Responsive browser console, dashboard, transcript export |
| `build_sweepweave.mjs` | Canonical reproducible compiler and structural validator |
| `sweepweave_builder.mjs` | Backward-compatible export alias for existing tools |
| `export_sweepweave.mjs` | Source-to-export regeneration and exact drift check |
| `storyworld.json` | Compiled native artifact: 105 encounters, 10 spools, 261 options, 548 reactions |
| `engine.test.mjs` | Browser engine and deterministic war/peace regression fixtures |
| `native_rehearsal.test.mjs` | Seeded native path traversal and terminal eligibility assertions |

## Campaign structure

| Year | Act | International development | Fitna and AI conflict |
| --- | --- | --- | --- |
| 2034 | The Two Testimonies | Dakar solar waqf, tariffs and community ownership | Converted and unconverted Party factions; the first diplomatic oracle |
| 2035 | The Xinjiang Reckoning | Southeast Asian monsoon insurance and local sovereignty | Hui/Uyghur civic representation and an erroneous automated census |
| 2036 | The Persian Pivot | Trans-Indus water rights and shared aquifers | Competing ideas of free will; autonomous maritime escorts |
| 2037 | The House of Disputation | Niger Basin agriculture, open standards and debt | Six competing rationalist schools and a treaty model with a false assumption |
| 2038 | Gaza's Ledger | Grain deliveries through the Horn of Africa | Green Crescent militias; a fabricated AI ceasefire may start world war |
| 2039 | The Strait Ledger | Refugee-controlled development bank | Rival rationalist student councils; autonomous financial agents intensify the conflict |
| 2040 | The Green Schism | Refugee grids and desalination | Three Party and religious fitnas; the Human Command Tribunal |
| 2041 | Conference of the Ummah | A reconstruction parliament in Manila, Dakar and Baghdad | Samarkand's counter-council; a machine-issued ultimatum with stale delegated authority |

Each annual act contains seven policy encounters, followed by a diplomatic crisis. Failed bargaining can trigger a second brinkmanship exchange. The final four acts include branching war and peace chapters. Actual war episodes can be de-escalated; accumulated strategic pressures can also reignite a war after a ceasefire. A machine-generated claim can receive legal and political force when a government accepts an earlier delegation of authority without re-verifying its scope.

### Systemic dynamics

State values remain within **[-1, +1]** and are displayed as percentages of the signed range. The authored metrics are:

- **U** Ummah consent; **A** rationalist credibility; **L** religious liberty; **M** Mihna coercion; **P** Party cohesion.
- **D** development equity; **W** civilian welfare; **T** trade resilience; **H** humanitarian displacement.
- **C** AI command integrity; **G** world-war intensity; **B** brinkmanship; **S** strategic prestige; **F** internal fitna.
- **V/Q** perceived consent and perceived rationalist credibility, which may diverge from reality.

Coercive doctrines and restrictions on conscience can intensify fitna; equitable development helps communities and reduces displacement. Weak AI authorization increases military escalation risk. A growing world war displaces civilians and harms welfare. The game records these secondary effects separately from the visible policy choice.

From 2038 onward, a global war chapter becomes active when `G >= 0.26`, `C <= -0.24`, or `B >= 0.58`. The alternatives are peace chapters concerned with verification, arms restraint and rebuilding confidence. Further escalation can lead to an irreversible catastrophe.

### End states

There are fifteen endings: **The Fifth Article**, **A Council of Equals**, **The People's Reconstruction**, **The Red Mihna**, **The Paper Caliphate**, **The Mandarin Crescent**, **The Free Cities of Kalam**, **A Cold War of Fatwas**, **The Strategic Retreat**, **The Map Turns Black**, **The Unfinished Mandate**, **The Southern Development Covenant**, **The Machine Armistice**, **The Fractured Ummah**, and **The War of Oracles**.

Each ending has an explicit eligibility rule. An authored score ranks only eligible terminal futures. The Unfinished Mandate remains eligible if no other future satisfies the state conditions.

## Build and tests

Run from this folder after installing Node 18+:

```sh
node --test engine.test.mjs native_rehearsal.test.mjs
node export_sweepweave.mjs --check
```

Recompile after editing `source_cards.json`:

```sh
node export_sweepweave.mjs
```

Validate with the repository's Sweepweave script from this folder:

```sh
python ../../codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworld.json
```

The authored source and native compiler have been checked structurally. Two independent simulated runs of **5,000 seeded playthroughs each** traversed the browser rules and the generated native encounter graph. Both reached all fifteen endings, with no missing targets, timeouts or disallowed terminal outcomes; no ending exceeded 20% in the browser rehearsal and 19% in the native rehearsal. War and peace routes were both exercised.

These are deterministic structural and balance rehearsals. They provide no calibrated predictions about real international politics, conflict likelihood or theological developments. Execution of the checked-in Node tests on a local machine, a manual playthrough in `storyworld_reader.html`, and accessibility review remain release checks.

## Design notes

The strategic inspiration is Chris Crawford's *Balance of Power*, particularly obligations, threat escalation, credibility and the possibility that a diplomatic contest ends in catastrophe. This storyworld uses original characters, prose, state variables, choices and implementation.

The theological inspiration is classical Muʿtazilī argument about divine justice, human responsibility, rational inquiry and the created Qur'an. The historical Mihna serves as a warning about compulsory assent. Participants from China, the Muslim world and local communities can challenge Beijing's assumptions and refuse its authority.

This is alternate-history fiction. It does not assert that the real CCP has converted, that a particular religious movement has a mandate to govern Muslim societies, or that a world war is expected to occur.
