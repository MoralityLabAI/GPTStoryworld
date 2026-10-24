# Balance of Reason: The Red Mihna

**Alternate-history geopolitical storyworld | 2034–2041 | Fiction, not a forecast**

The Chinese Communist Party has undergone an impossible constitutional conversion, embracing Muʿtazilī theology and announcing its ambition to lead the **Ummah**. The player is **Secretary Lin Wenqi**, tasked with converting a declaration into a durable political order. Military deterrence, factories, religious institutions, and the daily lives of believers all exert pressure.

A politician can announce that the Qur'an is created. A scholar can reject the claim. An industrial superpower cannot make a global community consent by changing a sentence in its Party constitution.

## Play

From this folder, serve the static browser edition:

```bash
python -m http.server 8000
```

Open **http://localhost:8000** and play with a browser. The game has no external JavaScript dependencies. The **analyst mode** checkbox reveals approximate state changes; otherwise, choices conceal their precise effects. Keyboard keys **1–3** select policy options. **Export decision trace** downloads a JSON record of every decision and the evolving state.

For direct use with GPTStoryworld's existing Sweepweave reader, open the repo-root **`storyworld_reader.html`** in a browser and load **`storyworlds/balance_of_reason/storyworld.json`** with its file picker. The two play surfaces derive from the same authored cards and use matching crisis thresholds.

## Files

| Path | Purpose |
| --- | --- |
| `source_cards.json` | Editable story: eight annual acts, 32 policy scenes, eight incident dossiers, all endings |
| `engine.mjs` | Pure, deterministic choice, state, and escalation engine for the standalone game |
| `index.html` | Original browser UI with theatrical briefings, faction meters, and trace export |
| `sweepweave_builder.mjs` | Compiler into the repo's standard encounter/spool schema |
| `export_sweepweave.mjs` | Rebuild the generated JSON, or check for drift |
| `storyworld.json` | Compiled 60-encounter, 10-ending Sweepweave storyworld |
| `engine.test.mjs` | Shape, reachability, reproducibility, and seeded rehearsal tests |

Run from this folder:

```bash
node --test engine.test.mjs
node export_sweepweave.mjs --check
```

To regenerate the compiled world after editing the source:

```bash
node export_sweepweave.mjs
```

Requires Node 18+ for the test runner and ES modules.

## Rules of the crisis board

Each **year** has four authored policy decisions and a diplomatic incident. The player can seek verified compromise, apply strategic pressure, or back down with stated reasons. An unresolved challenge advances to a second, higher-stakes standoff. A renewed military alert can trigger a catastrophic terminal outcome; backing down damages prestige and preserves the future.

This borrows the **crisis / prestige / brinkmanship** logic of Chris Crawford's *Balance of Power*, while adding domestic religious freedom, perceived versus actual consent, civilian consequences, and the problem of legitimacy that diplomacy alone cannot solve.

- **U:** Ummah Consent. Independent Muslim actors' willingness to participate.
- **A:** Rationalist Credibility. Whether the program is compatible with inquiry, evidence, and scholarly independence.
- **L:** Religious Liberty. Effective rights to worship, dissent, and appeal state actions.
- **W:** Civilian Welfare. Health, aid distribution, safety, and infrastructure outcomes.
- **P:** Party Cohesion. Ability to sustain the program inside the converted CCP.
- **T:** Trade Resilience. Energy, payments, shipping, and industrial redundancy.
- **S:** Strategic Prestige. International credibility of commitments and deterrence.
- **B:** Brinkmanship. Accumulated escalation risk; a high late-stage alert can end the simulation.
- **M:** Mihna Coercion. The temptation to test religious belief through state authority.
- **V / Q:** Perceived Consent / Perceived Credibility. Public reputation, which can diverge from actual experience.

All metrics are bounded **[-1,+1]**. The scenario is a **designed interactive fiction**, with authored coefficients representing narrative tensions rather than measured empirical causal effects. The browser edition is deterministic for the same sequence of decisions. Trace export supports repeatability and agent-forecast experiments.

## The theological conflict

The story draws on the classical Muʿtazilī five principles: divine unity (*tawḥīd*), divine justice (*ʿadl*), the promise and threat (*al-waʿd wa'l-waʿīd*), the intermediate position (*al-manzila bayna'l-manzilatayn*), and commanding right and forbidding wrong (*al-amr bi'l-maʿrūf wa'l-nahy ʿan al-munkar*).

The historical **Mihna** raises the central institutional contradiction. If government officials compel citizens and scholars to affirm the created Qur'an, a supposedly rationalist public order has adopted coercive orthodoxy. That conflict is directly playable in Act VII.

The Ummah consists of diverse peoples, schools, governments, and religious organizations. In this story, China can request leadership, fund shared institutions, or demand allegiance. Muslim characters and institutions can refuse without their refusal being treated as mechanically illegitimate. Uyghur and Hui voices, Palestinian civilian institutions, and independent international scholars have decision-making importance beyond their strategic value to China.

## Eight acts

| Year | Act | Principal pressure |
| --- | --- | --- |
| 2034 | The Two Testimonies | Conversion of the Party; consent versus proclamation |
| 2035 | The Xinjiang Reckoning | Local religious liberty, missing records, due process |
| 2036 | The Persian Pivot | Iran, Gulf partnerships, shipping and dual-use aid |
| 2037 | The House of Disputation | Cairo, scholarly independence and the created Qur'an |
| 2038 | Gaza's Ledger | Palestinian-led reconstruction and dual-use exports |
| 2039 | The Strait Ledger | Hormuz energy risk and escalation through ambiguity |
| 2040 | The Green Schism | A second Mihna or a right to theological dissent |
| 2041 | The Conference of the Ummah | Independent ballots and the permanent-chair dispute |

The ten endings include the **Fifth Article**, the **Council of Equals**, the **People's Reconstruction**, the **Red Mihna**, a **Paper Caliphate**, commercial predominance, a free network of academies, doctrinal cold war, strategic retreat, and catastrophic escalation.

## Playtesting and limits

The initial 5,000 seeded, randomly chosen playthroughs of the compiled Sweepweave graph returned **zero missing targets, dead ends, or timeouts**, with **all ten endings reachable**. The largest ending accounted for about **22%** of simulated paths. The game has **60 encounters**, **149 options**, and **314 conditional reactions**.

These simulations test graph integrity and basic ending reachability. They do not establish realism, calibrated probabilities, or finished narrative pacing. Manual browser playtesting, adversarial role play, accessibility review, and comparison between the Sweepweave and browser readers remain valuable next steps.

## Intellectual references

- Chris Crawford, [*Balance of Power*, Chapter 5: Crises](https://erasmatazz.com/library/my-books/balance-of-power-the-book/chapter-5-crises.html), for obligation, danger, prestige, and crisis reasoning.
- Chris Crawford, [Chapter 8: How *Balance of Power* Was Created](https://www.erasmatazz.com/library/my-books/balance-of-power-the-book/chapter-8-how-balance-of.html), for the alternating diplomatic challenge that becomes a playable mechanic.
- The repo's existing `storyworld_format_guide.md`, `storyworlds/mihna_constitutional_alignment.json`, and `codex-skills/storyworld-building/SKILL.md` for schema and creative constraints.

All principal dialogue and named characters in this scenario are fictional. No real-world conversion or governance claim is asserted.
