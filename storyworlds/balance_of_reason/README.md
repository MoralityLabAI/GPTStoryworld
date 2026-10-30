# Balance of Reason: The Red Mihna

**Alternate-history geopolitical strategy | 2034–2041 | 11 independent factions | AI world war | internal fitnas**

In this fictional timeline the Chinese Communist Party converts to Muʿtazilī theology and declares that it will lead the Ummah. Secretary Lin Wenqi, the player, controls Beijing's policy yet must negotiate with institutions that retain their own authority, incentives, and willingness to defect. China's industrial capacity finances hospitals, energy systems, ports and universities worldwide. Its AI-based strategic systems can also turn unauthenticated diplomatic assertions into war.

The game is built around a question that makes the historical **Mihna** relevant again: what becomes of rational inquiry when a government insists on enforcing the correct creed?

## Public playtest

**[Play Balance of Reason on GitHub Pages](https://moralitylabai.github.io/GPTStoryworld/)**. GitHub's `gh-pages` deployment workflow has completed successfully. You can also run the site locally.

The illustrated title screen offers **New campaign**, **Resume campaign**, **How to play**, and **Copy playtest link**. During a game, **Copy campaign link** creates a compact URL containing the policy decisions made so far. Opening it on another device reconstructs the national and faction state against the same `source_cards.json` version. Players with an existing autosave are asked before replacing it. The copied URL contains policy decisions and a non-cryptographic compatibility checksum, with no feedback responses or personal details.

The **Feedback** screen can copy a field report and reproducible campaign link in one message, or download a JSON report. The player chooses what to share. No server receives playtest feedback.

### Install the original art and play offline

The title menu now has **Load pixel-art ZIP**. Select `balance-of-reason-production-art-pack.zip` directly, without extracting it or uploading anything to GitHub. The browser verifies seven WebP images and stores the full-resolution artwork locally with IndexedDB. You can replace it or use **Restore default SVG artwork** from the Gallery. Artwork stays on the same device and is independent of shared campaign links.

The game also registers an offline cache on HTTPS and localhost. After one successful online visit, the campaign engine, scenes, map, and saved local progress can be used without a network connection. New storyworld editions still require an online refresh. The imported art remains available offline on browsers that allow local storage.

## Play in a browser

From this directory, start a local web server:

```sh
python3 -m http.server 8000
```

Visit **http://localhost:8000**. Choose policy options with the mouse or keys **1**, **2**, or **3**. The national dashboard displays 16 bounded indicators while the coalition board shows 11 independently motivated constituencies. The highlighted faction has a chance to issue a countermove that year.

**Copy campaign link** shares the reproducible policy history through a URL. **Save trace** exports the decisions, outcomes, 16 national scores and 11 coalition standings. **Resume trace** loads the record, verifies every turn against the same `source_cards.json` revision, and reconstructs the exact active scene. A compatibility fingerprint guards against accidentally resuming on an altered edition; this is a consistency check rather than a cryptographic authentication mechanism.

**Export Sweepweave JSON** generates the full-metadata native storyworld in the browser. Open the repo-root `storyworld_reader.html` and select that JSON file to play it in the existing reader.

## Campaign map

| Year | Development and diplomacy | Internal fitna | AI and armed crisis | Institutional countermove |
| --- | --- | --- | --- | --- |
| 2034 | Dakar solar waqf and the conversion congress | Marxist veterans dispute obligatory conversion | The diplomatic oracle invents endorsements | Unconverted Convention |
| 2035 | Philippine monsoon insurance and rights in Xinjiang | Hui and Uyghur councils demand accountable representation | Automated census falsely identifies dissidents | Kashgar Appeal |
| 2036 | Water rights in the Indus basin and the Iran-Gulf balance | Rival interpretations of free will and justice | Autonomous maritime escorts and opaque threat models | Tehran refuses the escort clause |
| 2037 | Niger Basin agriculture, debt and local ownership | Six competing rationalist schools | The AI-modeled treaty assumes away political agency | Kufa-Cairo Counterfatwa |
| 2038 | Gaza and Horn of Africa humanitarian logistics | Green Crescent militants try to police doctrine | A fabricated ceasefire initiates the World War of the Models | Palestinian reconstruction veto |
| 2039 | Refugee-managed infrastructure bank and global supply chains | Two rival campus caliphates | Autonomous financial agents harden sanctions and war logistics | Gulf war-premium refusal |
| 2040 | Microgrids and desalination for displaced communities | The Three Fitnas divide the Party, clergy and provincial councils | Human Command Tribunal addresses AI military responsibility | Second-Mihna ultimatum |
| 2041 | Reconstruction parliament in Manila, Dakar and Baghdad | Samarkand's Counter-Council challenges Beijing | A stale digital delegation creates a machine-issued ultimatum | Shura recall petition |

Each of the eight acts contains seven authored policy scenes, an **independent faction countermove**, and an escalating diplomatic crisis. During 2038–2041 a world-war threshold chooses an armed-conflict chapter or fragile-peace chapter. The threat of catastrophic escalation can end the simulation before the Istanbul assembly convenes.

### Strategy system

The 16 signed values, each bounded to [-1,+1], model real and perceived consent, political authority, individual liberties, welfare, trade, development equity, strategic prestige, coercion, internal factionalism, AI command integrity, brinkmanship, war intensity and displacement.

Eleven factions maintain their own `Coalition_Standing` values. They include China's secular Party veterans and security establishment, Uyghur and Hui councils, independent rationalist academies, a transnational Muslim shura, Iranian and Gulf institutions, Palestinian reconstruction authorities, Atlantic security representatives, the development ministries, and the coercive Green Crescent Vanguard. Every faction has its own stated mandate and weighted policy interests.

An annual countermove responds to the faction's actual accumulated support. It may cooperate or organize resistance even when the player selects the same diplomatic response. Decisions that strengthen Party control can deepen fitna; development may reduce displacement; permissive AI command systems can increase war intensity. These are **fictional causal coefficients for strategic play**, with no claim of calibrated geopolitical probabilities.

The fifteen possible endings include a deliberative Council of Equals, a coercive Red Mihna, a Southern Development Covenant, the Machine Armistice, the Fractured Ummah, a continuing War of Oracles, and the catastrophic Map Turns Black.

## Source, readers and export formats

| File | Role |
| --- | --- |
| `source_cards.json` | Canonical v3 storyworld: eight acts, countermoves, eleven constituencies, fifteen endings |
| `engine.mjs` | Browser strategic engine with persistent faction scores and an AI-war state machine |
| `index.html` | Playable responsive browser game, coalition dashboard and native export control |
| `trace_protocol.mjs` | Source-pinned save/replay protocol validating every recorded choice and state |
| `build_sweepweave.mjs` | Full-metadata native compiler for local editor/Godot workflows |
| `compact_sweepweave.mjs` | Behavior-preserving projection for the JavaScript reader |
| `sweepweave_builder.mjs` | Reader-ready export wrapper for tests and committed `storyworld.json` |
| `export_sweepweave.mjs` | Regenerates the compact reader artifact or checks it for drift |
| `storyworld.json` | **113 encounters, 10 spools, 285 options, 596 reactions**, generated from v3 source |
| `*.test.mjs` | Engine, cross-surface parity, native rehearsal and trace-integrity tests |

The checked-in `storyworld.json` is a compact representation for this repository's JavaScript reader. It omits redundant expression metadata and uses simplified, logically equivalent conditional reaction weights. The **full metadata** version can be generated with `node build_sweepweave.mjs` or the browser's **Export Sweepweave JSON** button. Validate Godot/editor-specific parsing separately if that external editor is the destination.

## Validation and reproducibility

From this directory, with Node 18+:

```sh
node --test *.test.mjs
node export_sweepweave.mjs --check
```

From the repository root:

```sh
python3 codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworlds/balance_of_reason/storyworld.json
```

The CI workflow at `.github/workflows/balance-of-reason.yml` runs these checks automatically on relevant commits. The parity test walks 300 deterministic browser/native policy traces. The native and browser rehearsals each sample 5,000 strategies for ending reachability and stability. The trace protocol test replays another 250 campaigns and challenges altered history, faction states, incorrect source revisions and choice indices.

Automated checks establish structural and deterministic consistency. They do not establish historical plausibility, military realism, or a well-paced experience in every reader. Manual browser and accessibility review remain appropriate before release.

## Intellectual framing

Chris Crawford's *Balance of Power* provides the crisis logic: backing down carries reputational costs and escalating a threat risks catastrophe. The world adds civilian reconstruction, independent religious authority, internal political schisms and machine-mediated uncertainty.

Its Muʿtazilī material draws on the five classical principles, including divine unity, justice, responsibility, and commanding right and forbidding wrong. The possibility of another Mihna asks how a rationalist state behaves when the people it claims to protect decline its interpretation. Local Muslim and secular institutions can reject Beijing's authority without being written out of the political system.

Everything after the fictional 2034 conversion is alternate history. This work asserts neither a CCP conversion nor a forecast of world war.

## Playtest chapters

The illustrated main menu offers three ready-to-play later chapters. Each one replays a genuine, source-pinned history through the normal engine, preserving national indicators, eleven faction standings, AI command integrity and the player's recorded choices. They provide short sessions for testing the most consequential scenes.

- **2038, The False Ceasefire:** a constructed diplomatic report tests command oversight and the risk of machine-initiated conflict.
- **2040, The Three Fitnas:** the Party, independent scholars and provincial councils dispute religious and constitutional authority.
- **2041, The Last Machine Ultimatum:** a delegated digital signature presents a final wartime authorization crisis.

Preview campaigns can be played through to an ending and shared by URL or the regular saved-trace format. When an existing autosave is present, opening a chapter asks for permission before replacing it. Presets live in `playtest_chapters.mjs` and are validated by `playtest_chapters.test.mjs`.

## Playtest comfort and production artwork

Players can now see a **Policy consequences** panel after each decision. It shows changes since the previous turn to national indicators and independent faction standings. The same impact ledger is reconstructed when saved campaign traces are resumed.

The generated high-resolution concept art is distributed as a seven-image WebP ZIP. The repo includes `tools/install_art_pack.py`, an archive-validated installer with automated tests, and a detailed guide at [assets/README.md](assets/README.md). An owner-run installation from a local checkout will publish those binaries to the PR and `gh-pages` branches. Until then, the live game uses the already-integrated vector illustrations.

## Illustrated GitHub Pages playtest (production frontend preview)

The visual frontend is implemented in `visuals.mjs` and `visuals.css`, loaded by the existing `index.html`. It provides an illustrated title/menu, contextual portraits, a clickable regional atlas, diplomacy view, an institutional policy codex, chronicle, gallery, responsive mobile layout and playtest feedback download. The original strategic engine still governs every choice and faction countermove.

The project also has a clean **`gh-pages`** branch containing a root-level static copy of the site and four self-contained illustrated SVG backdrops. The repository owner can enable the public playtest at **[Repository Settings → Pages](https://github.com/MoralityLabAI/GPTStoryworld/settings/pages)**: choose **Deploy from a branch**, select **`gh-pages`** and **`/(root)`**, then Save. The intended site URL is **https://moralitylabai.github.io/GPTStoryworld/**. The Pages build-and-deploy workflow has completed successfully for `gh-pages`; the published link above is intended for playtesting.

The browser can import the ZIP directly using **Load pixel-art ZIP**. Repository-wide hosting of the same artwork is also supported by placing the optional files in `assets/`: `hero.webp`, `warroom.webp`, `summit.webp`, `world.webp`, `dialogue.webp`, `ceasefire.webp` and `characters.webp`. The browser automatically uses each WebP when present and falls back to a locally hosted SVG scene otherwise. The actual interactive map pins, policy options, stats and dialogue text remain accessible HTML rather than text baked into generated images. See `assets/README.md` for installation.

The app autosaves an indexed, *deterministic* decision trace to the current browser's local storage. **Resume campaign** restores that local save, and **Save trace / Resume trace** exports or imports it as JSON. The revision fingerprint checks game compatibility rather than certifying authenticity.

Tests include:
- `node --test *.test.mjs` for storyworld parity, gameplay, portraits, atlas, trace integrity and source-pinned shareable campaigns.
- `node browser-smoke.mjs` using a local Chrome/Chromium and `playwright-core` to verify the real UI from title screen through decisions, autosave/resume, mobile and feedback.
- `.github/workflows/balance-of-reason-pages.yml` stages the playtest build after regression and headless browser checks. Branch deployment through `gh-pages` is the default. Optional GitHub Actions deployment can be enabled later.

The site is a public fictional-playtest build. Art imports, campaign autosaves, and feedback remain on the player's device unless they choose to share. A small, versioned service worker supports repeat visits offline.
