# HUD/Menu Scripting Guide

## Purpose
This guide documents how to stage Quake Live HUD and menu assets inside the GPL tree, automate regeneration, and uphold accessibility guarantees while iterating on scripts.

## Asset Workflow Overview
### 1. Establish the Source of Truth
- Treat `assets/quakelive/baseq3/ui` as the canonical snapshot for `.menu`/`.txt` definitions, metadata tables, and supporting enums.
- Mirror every definition into `src/ui`, including locale tables (`country.txt`, `teaminfo.txt`) and the full set of HUD presets (`hud.txt`, `hud2.txt`, `hud3.txt`). Use the audit spreadsheet to flag any drift between trees.

### 2. Sync Menu Definitions and Metadata
- Copy missing files into `src/ui`, preserving path casing.
- Keep GPL-only helpers (`credential.menu`, `ingame_quakelive.txt`, `menus_quakelive.txt`) but reconcile their dependencies so they reference the restored assets instead of temporary fallbacks.
- Diff the staged files against upstream Quake Live revisions before shipping changes to maintain behavioural parity.

### 3. Stage Art, Fonts, and Shaders
- Import the entire `ui/assets` hierarchy into a reproducible bundle (for example `pak_uiql.pk3`). This includes HUD chrome, score state textures, menu backgrounds, and national flags.
- Point the font bake step at `assets/quakelive/baseq3/fonts/` so the canonical Quake Live TTFs (`handelgothic.ttf`, `notosans-regular.ttf`, `droidsansmono.ttf`, `droidsansfallbackfull.ttf`) remain intact in their original location. Treat this directory as the staging input for packaging rather than copying the binaries elsewhere.
- Run the font bake tool (`tools/packaging/bake_fonts.py`, invoked automatically by `tools/build_ui_bundle.sh`) against the staged TTFs to regenerate `fonts/font`, `fonts/smallfont`, `fonts/bigfont`, and `fonts/monofont` atlases that match scripted `textscale` expectations. The bake requires the FreeType Python bindings (`python3 -m pip install freetype-py`) to rasterize each TTF into `.tga` atlases during the build; the outputs live under `build/ui_bundle/staging/fonts/` and are not checked into the repo. `handelgothic.ttf` feeds the default `font`/`bigFont` look, `notosans-regular.ttf` drives the `smallFont` text blocks, `droidsansmono.ttf` is used for mono UI widgets, and `droidsansfallbackfull.ttf` keeps multilingual glyphs available for HUD prompts. Metrics for every bake land in `artifacts/ui_bundle/metrics/font_metrics.json` so CI can spot glyph drift.
- **License handling:** Handel Gothic is proprietary; only use the TTF and generated atlases for Quake Live compatibility testing, and avoid redistributing those artifacts outside the local build output. Droid Sans and Noto Sans remain under Apache 2.0.
- Bring over the `ui*.shader` files and any dependent materials so gradients, cursors, and overlay effects compile correctly.

### 4. Package the Assets
- Extend the data build to archive scripts, art, fonts, and shaders into a deterministic PK3. Keep the packaging recipe under version control (e.g., `tools/build_ui_bundle.sh`, which now copies the manifest inputs, calls the bake step, and writes `build/ui_bundle/pak_uiql.pk3`).
- Track packaging manifests under `tools/` so the bundle recipe is auditable. `tools/packaging/ui_bundle_manifest.json` now lists the Quake Live font binaries sourced from `assets/quakelive/baseq3/fonts/`, the paths they must occupy inside the PK3 (`fonts/*.ttf`), their HUD roles (`font`, `smallFont`, `bigFont`, `mono`), and the license caveats (Handel Gothic remains proprietary, while the Droid and Noto families stay under Apache 2.0).
- Version PK3 outputs or manifests to ensure reproducibility across Windows, macOS, and Linux builds.

### 5. Validate In-Game
- Launch with a clean homepath to ensure newly packaged assets are picked up rather than stale caches. `tests/run_ui_validation.py` automates this by creating `build/ui_validation/home`, extracting the bundle, and parsing representative HUD/menu panels for font references.
- Exercise HUD preset rotation, scoreboard variants, and menu navigation to confirm art, fonts, and locale tables resolve correctly. The validation harness checks `hud*.txt`/`*.menu` fonts plus shader handles, then uploads `artifacts/ui_validation/logs/ui_validation_summary.json` for CI triage.
- Capture screenshots of critical panels (scoreboards, spectator overlays, country dropdowns) to document parity checks. When headless captures are sufficient, store glyph metrics or shader summaries next to the bundle artefacts for reviewers.

## Automation & Tooling Tips
- Script the copy, font bake, shader sync, and packaging steps so contributors can regenerate the bundle with a single command (`tools/build_ui_bundle.sh` today; wire it into your preferred build front-end as `make ui-bundle`).
- Add linting scripts that scan `.menu` files for invalid `ownerdrawflag`, `showCvar`, and asset path references before packaging.
- Integrate the automation into CI so every commit that touches HUD assets runs rebuild and validation steps. The `UI Validation` workflow now executes the bundle builder followed by `tests/run_ui_validation.py`, uploads logs/metrics, and fails when glyph counts or shader handles drift.

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
- [ ] `tools/build_ui_bundle.sh` completes without error and `python tests/run_ui_validation.py` reports no glyph/shader drift.
- [ ] Accessibility guidelines (redundant cues, locale support, typography) are verified during manual QA.
- [ ] Documentation and commit messages capture any deviations from Quake Live defaults or new accessibility accommodations.
