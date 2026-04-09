# HUD/Menu Scripting Guide

## Purpose
This guide documents how to stage Quake Live HUD and menu assets inside the GPL tree, automate regeneration, and uphold accessibility guarantees while iterating on scripts.

## Asset Workflow Overview
### 1. Establish the Source of Truth
- Treat `assets/quakelive/baseq3/ui` as the canonical snapshot for `.menu`/`.txt` definitions, metadata tables, and supporting enums.
- Treat `src/ui` as a frozen mirror, not an active authoring surface. Use the audit notes and parity tests to flag drift between `src/ui` and the retail snapshot, then correct the drift through layered overrides rather than direct edits.

### 2. Sync Menu Definitions and Metadata
- Verify the staged retail corpus first with `scripts/ui/check_retail_ui_corpus.py`. The check writes `artifacts/ui_bundle/ui_retail_inventory.json`, reports all missing manifest-tracked `baseq3` inputs in one pass, and lets the UI parity tests switch cleanly between strict compare mode and actionable environment-warning mode.
- For frozen `src/ui` drift, generate retail-correct replacements with `scripts/ui/write_retail_ui_overrides.py` instead of patching files in place.
- Treat the generated overlay as the only writable correction layer for `src/ui`: `src/ui` stays the read-only baseline, `pak_uiql.pk3` remains the lower-priority base bundle, and `pak_ui_src_retail_overlay.pk3` is mounted from `fs_homepath/baseq3` so drifted files win without mutating the source tree.
- Do not rely on same-directory PK3 alphabetical order to make the overlay win. The supported contract is a separate `fs_homepath` layer above the lower-priority base bundle roots (`fs_basepath` / `fs_cdpath`).
- Keep GPL-only helpers (`credential.menu`, `ingame_quakelive.txt`, `menus_quakelive.txt`) but reconcile their dependencies so they reference the restored assets instead of temporary fallbacks.
- Diff the staged files against upstream Quake Live revisions before shipping changes to maintain behavioural parity, and record the known drift set in the audit docs/tests.

### 3. Stage Art, Fonts, and Shaders
- Import the entire `ui/assets` hierarchy into a reproducible bundle (for example `pak_uiql.pk3`). This includes HUD chrome, score state textures, menu backgrounds, and national flags.
- Point the font bake step at `assets/quakelive/baseq3/fonts/` so the canonical Quake Live TTFs (`handelgothic.ttf`, `notosans-regular.ttf`, `droidsansmono.ttf`, `droidsansfallbackfull.ttf`) remain intact in their original location. Treat this directory as the staging input for packaging rather than copying the binaries elsewhere.
- Run the font bake tool (`tools/packaging/bake_fonts.py`, invoked automatically by `tools/build_ui_bundle.sh`) against the staged TTFs to regenerate `fonts/font`, `fonts/smallfont`, `fonts/bigfont`, and `fonts/monofont` atlases that match scripted `textscale` expectations. When the FreeType Python bindings are available (`python3 -m pip install freetype-py`), the tool rasterizes each TTF into `.tga` atlases during the build. When FreeType is unavailable, the tool still emits deterministic `.dat` metadata, placeholder `.tga` atlas files, and the expected metrics payload so CI/bundle generation can proceed without blocking on an external wheel. `handelgothic.ttf` feeds the default `font`/`bigFont` look, `notosans-regular.ttf` drives the `smallFont` text blocks, `droidsansmono.ttf` is used for mono UI widgets, and `droidsansfallbackfull.ttf` keeps multilingual glyphs available for HUD prompts. Metrics for every bake land in `artifacts/ui_bundle/metrics/font_metrics.json` so CI can spot glyph drift.
- **License handling:** Handel Gothic is proprietary; only use the TTF and generated atlases for Quake Live compatibility testing, and avoid redistributing those artifacts outside the local build output. Droid Sans and Noto Sans remain under Apache 2.0.
- Bring over the `ui*.shader` files and any dependent materials so gradients, cursors, and overlay effects compile correctly.

### 4. Package the Assets
- Extend the data build to archive scripts, art, fonts, and shaders into a deterministic PK3. Keep the packaging recipe under version control (e.g., `tools/build_ui_bundle.sh`, which now copies the manifest inputs, calls the bake step, and writes `build/ui_bundle/pak_uiql.pk3`).
- The bundle preflight now runs `scripts/ui/check_retail_ui_corpus.py --strict` first, so missing retail configs, fonts, shaders, menus, icons, and levelshots are reported together before packaging starts.
- The same build flow now emits `build/ui_bundle/pak_ui_src_retail_overlay.pk3`, a layered package containing only the retail-correct replacements for the frozen `src/ui` drift set.
- `artifacts/ui_bundle/ui_src_retail_overlay.json` now records the overlay policy, the deterministic hash and size for every overlaid file, and stale-file cleanup evidence so CI can verify the package contains all and only the active drift set.
- Track packaging manifests under `tools/` so the bundle recipe is auditable. `tools/packaging/ui_bundle_manifest.json` now lists the Quake Live font binaries sourced from `assets/quakelive/baseq3/fonts/`, the paths they must occupy inside the PK3 (`fonts/*.ttf`), their HUD roles (`font`, `smallFont`, `bigFont`, `mono`), and the license caveats (Handel Gothic remains proprietary, while the Droid and Noto families stay under Apache 2.0).
- Version PK3 outputs or manifests to ensure reproducibility across Windows, macOS, and Linux builds.

### 5. Validate In-Game
- Launch with a clean homepath to ensure newly packaged assets are picked up rather than stale caches. `tests/run_ui_validation.py` automates this by creating `build/ui_validation/home`, extracting the bundle, and parsing representative HUD/menu panels for font references.
- Exercise HUD preset rotation, scoreboard variants, and menu navigation to confirm art, fonts, and locale tables resolve correctly. The validation harness checks `hud*.txt`/`*.menu` fonts plus shader handles, then uploads `artifacts/ui_validation/logs/ui_validation_summary.json` for CI triage.
- Run `python -B -m pytest tests/test_ui_full_parity_gate.py -q` after the bundle and headless validation passes. The gate writes `artifacts/ui_validation/logs/ui_full_parity_gate.json`, summarises every UI gap tranche (`UI-G01`..`UI-G06`), and records an overall release-style pass/fail result.
- When a milestone run needs the gate to fail hard unless every tranche is green, set `UI_FULL_PARITY_GATE_ENFORCE=1` before invoking the test. In normal contributor runs the report is still written, but the strict release-mode assertion remains opt-in.
- Capture screenshots of critical panels (scoreboards, spectator overlays, country dropdowns) to document parity checks. For the current closure milestone, the tracked runtime evidence bundle is `artifacts/ui_validation/logs/ui_runtime_evidence_20260406.json`, which points to the main-menu and in-game flow captures plus the supporting logs.

## Automation & Tooling Tips
- Script the copy, font bake, shader sync, and packaging steps so contributors can regenerate the bundle with a single command (`tools/build_ui_bundle.sh` today; wire it into your preferred build front-end as `make ui-bundle`).
- Add linting scripts that scan `.menu` files for invalid `ownerdrawflag`, `showCvar`, and asset path references before packaging.
- Integrate the automation into CI so every commit that touches HUD assets runs rebuild and validation steps. The `UI Validation` workflow now executes the bundle builder, `tests/run_ui_validation.py`, and `tests/test_ui_full_parity_gate.py`, then uploads logs/metrics plus the unified gate report for tranche-level triage.

## Service-Disabled Menu Routing
- Treat the retail browser verbs reachable from menu scripts as an explicit routing matrix when `QL_BUILD_ONLINE_SERVICES=0` or no overlay provider is initialised.
- `exec web_showBrowser`: if invoked from the retail main menu, the writable runtime now opens the generated `ql_bridge_browser` surface instead of dispatching into the inert host stub; if the bridge cannot be loaded, the UI raises `error_popmenu` with a native fallback message.
- `exec web_showBrowser` from in-game lower-nav panels and `exec web_changeHash ...` from `intro.menu` or `ingame.menu` are swallowed locally when the overlay is unavailable, leaving the companion native menus (`ingame_about`, join controls, settings panels) active instead of hard-stopping on dead service commands.
- `uiScript stopRefresh` always stops the native server refresh path. The overlay-specific `web_stopRefresh` console command is only forwarded when the browser layer exists; otherwise the UI logs the offline-native fallback and keeps the browser list usable.
- Launcher-compatible local resource loads stay available even when live online services are disabled: the retained owner chain still checks `web.pak`, the mapped `fs_webpath` / `screenshots` fallback roots, and the non-Steam URI bridge before reporting a resource miss, so offline bridge menus and default advert content do not depend on the missing retail launcher host.
- `activateAdvert` stays implemented in offline builds through the advert shader fallback path and the advertisement wait-screen text export, so advert panels and wait states remain drawable even with online services disabled.

## Accessibility Considerations
- **Redundant Feedback:** Preserve the combination of color fills, icons, and numeric/textual owner-draws in score widgets to support colorblind players. If new art is introduced, provide contrast-checked variants and document the options.
- **Locale Coverage:** Ensure `country.txt` and `teaminfo.txt` remain in sync with localisation requirements so dropdowns expose textual identifiers alongside flag art.
- **Typography:** Validate that regenerated fonts remain legible at competitive HUD scales (1080p, 1440p, 4K). Adjust `textscale` only with QA sign-off and note any deltas in the change log.
- **Spectator Overlays:** Pair ink-fade textures with textual cues (player names, objective state, timers) to support screen readers and low-vision spectators.
- **Input Focus & Cursors:** Offer high-contrast cursor themes and highlight states, ensuring focus indicators are not solely color-dependent.
- **Documentation:** Log asset swaps, font regenerations, and accessibility reviews in commit messages or release notes so reviewers can trace decisions.

## Contribution Checklist
- [x] All Quake Live `.menu`/`.txt` files (including locale and HUD presets) are staged in `src/ui`.
- [ ] The frozen `src/ui` drift set is either unchanged and covered by the retail overlay package, or deliberately reduced with updated parity evidence.
- [ ] Art, fonts, and shader dependencies are packaged into a reproducible PK3 and referenced by the scripts.
- [ ] `tools/build_ui_bundle.sh` completes without error and `python tests/run_ui_validation.py` reports no glyph/shader drift.
- [ ] `python -B -m pytest tests/test_ui_full_parity_gate.py -q` writes `artifacts/ui_validation/logs/ui_full_parity_gate.json` and any non-passing tranche is understood before landing changes.
- [ ] Accessibility guidelines (redundant cues, locale support, typography) are verified during manual QA.
- [ ] Documentation and commit messages capture any deviations from Quake Live defaults or new accessibility accommodations.
