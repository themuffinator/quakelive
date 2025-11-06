# HUD/Menu Scripting Guide

## Purpose
This guide documents how to stage Quake Live HUD and menu assets inside the GPL tree, automate regeneration, and uphold accessibility guarantees while iterating on scripts.

## Asset Workflow Overview
### 1. Establish the Source of Truth
- Treat `references/original-assets/quakelive/baseq3/ui` as the canonical snapshot for `.menu`/`.txt` definitions, metadata tables, and supporting enums.
- Mirror every definition into `src/ui`, including locale tables (`country.txt`, `teaminfo.txt`) and the full set of HUD presets (`hud.txt`, `hud2.txt`, `hud3.txt`). Use the audit spreadsheet to flag any drift between trees.

### 2. Sync Menu Definitions and Metadata
- Copy missing files into `src/ui`, preserving path casing.
- Keep GPL-only helpers (`credential.menu`, `ingame_quakelive.txt`, `menus_quakelive.txt`) but reconcile their dependencies so they reference the restored assets instead of temporary fallbacks.
- Diff the staged files against upstream Quake Live revisions before shipping changes to maintain behavioural parity.

### 3. Stage Art, Fonts, and Shaders
- Import the entire `ui/assets` hierarchy into a reproducible bundle (for example `pak_uiql.pk3`). This includes HUD chrome, score state textures, menu backgrounds, and national flags.
- Copy Quake Live’s TTFs from `references/original-assets/quakelive/baseq3/fonts` and run the font bake tool to generate `fonts/font`, `fonts/smallfont`, and `fonts/bigfont` atlases that match scripted `textscale` expectations.
- Bring over the `ui*.shader` files and any dependent materials so gradients, cursors, and overlay effects compile correctly.

### 4. Package the Assets
- Extend the data build to archive scripts, art, fonts, and shaders into a deterministic PK3. Keep the packaging recipe under version control (e.g., `tools/build_ui_bundle.sh`).
- Version PK3 outputs or manifests to ensure reproducibility across Windows, macOS, and Linux builds.

### 5. Validate In-Game
- Launch with a clean homepath to ensure newly packaged assets are picked up rather than stale caches.
- Exercise HUD preset rotation, scoreboard variants, and menu navigation to confirm art, fonts, and locale tables resolve correctly.
- Capture screenshots of critical panels (scoreboards, spectator overlays, country dropdowns) to document parity checks.

## Automation & Tooling Tips
- Script the copy, font bake, shader sync, and packaging steps so contributors can regenerate the bundle with a single command (`make ui-bundle` target or similar).
- Add linting scripts that scan `.menu` files for invalid `ownerdrawflag`, `showCvar`, and asset path references before packaging.
- Integrate the automation into CI so every commit that touches HUD assets runs rebuild and validation steps.

## Accessibility Considerations
- **Redundant Feedback:** Preserve the combination of color fills, icons, and numeric/textual owner-draws in score widgets to support colorblind players. If new art is introduced, provide contrast-checked variants and document the options.
- **Locale Coverage:** Ensure `country.txt` and `teaminfo.txt` remain in sync with localisation requirements so dropdowns expose textual identifiers alongside flag art.
- **Typography:** Validate that regenerated fonts remain legible at competitive HUD scales (1080p, 1440p, 4K). Adjust `textscale` only with QA sign-off and note any deltas in the change log.
- **Spectator Overlays:** Pair ink-fade textures with textual cues (player names, objective state, timers) to support screen readers and low-vision spectators.
- **Input Focus & Cursors:** Offer high-contrast cursor themes and highlight states, ensuring focus indicators are not solely color-dependent.
- **Documentation:** Log asset swaps, font regenerations, and accessibility reviews in commit messages or release notes so reviewers can trace decisions.

## Contribution Checklist
- [ ] All Quake Live `.menu`/`.txt` files (including locale and HUD presets) are staged in `src/ui`.
- [ ] Art, fonts, and shader dependencies are packaged into a reproducible PK3 and referenced by the scripts.
- [ ] Automation scripts rebuild the HUD bundle end-to-end and run linting checks.
- [ ] Accessibility guidelines (redundant cues, locale support, typography) are verified during manual QA.
- [ ] Documentation and commit messages capture any deviations from Quake Live defaults or new accessibility accommodations.
