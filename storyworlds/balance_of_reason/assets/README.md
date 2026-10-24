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

## Production art installation

The generated art pack is distributed as **`balance-of-reason-production-art-pack.zip`**. It contains seven optimized WebP files with exact filenames matching the player.

From a checked-out `GPTStoryworld` repository:

```sh
python3 storyworlds/balance_of_reason/tools/install_art_pack.py /path/to/balance-of-reason-production-art-pack.zip --dry-run
python3 storyworlds/balance_of_reason/tools/install_art_pack.py /path/to/balance-of-reason-production-art-pack.zip
git add storyworlds/balance_of_reason/assets/*.webp storyworlds/balance_of_reason/assets/art_pack_manifest.json
git commit -m "Add generated Balance of Reason production art"
git push
```

On Windows, use `py -3` in place of `python3`. The installer checks archive paths, the seven required filenames, the WebP file headers, decompressed sizes and checksums. It writes an `art_pack_manifest.json` alongside the images. Re-running an unchanged pack is safe. Use `--replace` only to install a deliberately changed pack.

The active public playtest currently publishes from `gh-pages`. To update that branch, use a dedicated worktree after fetching it:

```sh
git fetch origin gh-pages
git worktree add ../bor-pages gh-pages
python3 storyworlds/balance_of_reason/tools/install_art_pack.py /path/to/balance-of-reason-production-art-pack.zip --target ../bor-pages/assets
git -C ../bor-pages add assets/
git -C ../bor-pages commit -m "Publish high-resolution Balance of Reason art"
git -C ../bor-pages push origin HEAD:gh-pages
```

If a local `gh-pages` branch is already checked out elsewhere, reuse that checkout rather than adding a second worktree. After GitHub's Pages deployment completes, the game automatically loads the new WebPs. The vector fallback stays in place for clients whose image request fails.

## Hosting

For a GitHub Pages branch deploy, add these WebPs to the root `assets/` folder on `gh-pages` and commit them there. For the main repo development branch, add them under `storyworlds/balance_of_reason/assets/`. Once merged, the repository's Pages build workflow stages the same directory structure.

The art is based on generated visual concept material for this fictional universe. The SVGs are deliberately compact and readable without remote image hosting, downloaded fonts or JavaScript dependencies.
