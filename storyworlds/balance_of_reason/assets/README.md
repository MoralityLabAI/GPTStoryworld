# Pixel art and scene assets

The illustration slots are already wired into `visuals.mjs`. SVG scenes in this directory provide a complete self-contained playable fallback for GitHub Pages.

## Optional rendered art overrides

Copy the following WebP files into this directory to use the concept art generated for this project. The frontend detects them and upgrades the visuals without changing any player logic.

| Optional file | Usage |
| --- | --- |
| `hero.webp` | Illustrated title screen featuring Secretary Lin Wenqi and faction representatives |
| `warroom.webp` | Beijing strategy room and standard policy scenes |
| `summit.webp` | International assembly and game endings |
| `world.webp` | Atlas backdrop behind accessible, interactive route pins |
| `dialogue.webp` | Negotiation scenes and autonomous faction countermoves |
| `ceasefire.webp` | Crisis and World War of the Models scenes |
| `characters.webp` | Gallery/reference illustration of principal characters |

The first WebP layer is decorative background art. All buttons, statistics, region names, policy labels, portraits, and faction rankings are rendered as real browser elements, using the authored source rather than image-generated typography.

## Hosting

For a GitHub Pages branch deploy, add these WebPs to the root `assets/` folder on `gh-pages` and commit them there. For the main repo development branch, add them under `storyworlds/balance_of_reason/assets/`. Once merged, the repository's Pages build workflow stages the same directory structure.

The art is based on generated visual concept material for this fictional universe. The SVGs are deliberately compact and readable without remote image hosting, downloaded fonts or JavaScript dependencies.
