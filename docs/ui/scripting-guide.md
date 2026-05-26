# HUD/Menu Scripting Guide

## Purpose
This guide documents how to stage Quake Live HUD and menu assets inside the GPL tree, automate regeneration, and uphold accessibility guarantees while iterating on scripts.

## Asset Workflow Overview
### 1. Establish the Source of Truth
- Treat `assets/quakelive/baseq3/ui` as the canonical snapshot for `.menu`/`.txt` definitions, metadata tables, and supporting enums.
- Treat `src/ui` as the read-only checked-in runtime-panel baseline, not an active authoring surface. The current `.menu`/`.txt` compare is clean (`65 / 65` files, `0` content diffs); if drift reappears, use the audit notes and parity tests to catch it and correct it through layered overrides rather than direct edits.

### 2. Sync Menu Definitions and Metadata
- Verify the staged retail corpus first with `scripts/ui/check_retail_ui_corpus.py`. The check writes `artifacts/ui_bundle/ui_retail_inventory.json`, reports all missing manifest-tracked `baseq3` inputs in one pass, and lets the UI parity tests switch cleanly between strict compare mode and actionable environment-warning mode.
- If `src/ui` drift reappears, generate retail-correct replacements with `scripts/ui/write_retail_ui_overrides.py` instead of patching files in place.
- Treat the generated overlay manifest as the default drift report, not as a default runtime package: `src/ui` stays the read-only baseline, normal contributor runs keep retail runtime PK3s unmaterialized, and the current manifest records an empty `drift_files` set on the clean worktree.
- The supported exception is an explicit runtime-refresh or probe flow that calls `tools/build_ui_bundle.py --runtime-root <writable baseq3>`, emits `pak_uiql.pk3`, emits the bounded `pak_ui_src_retail_overlay.pk3` only when `drift_files` is non-empty, and records `artifacts/ui_bundle/runtime_ui_package_manifest.json` as the verification contract.
- Do not leave repo-generated retail replacement PK3s in `fs_homepath` by default. Outside the explicit runtime-refresh/probe path above, the only files that should appear there are locally built DLLs, configs, logs, screenshots, and bridge files that do not duplicate retail distributables.
- Keep GPL-only helpers (`credential.menu`, `ingame_quakelive.txt`, `menus_quakelive.txt`) but reconcile their dependencies so they reference the restored assets instead of temporary fallbacks.
- Diff the staged files against upstream Quake Live revisions before shipping changes to maintain behavioural parity, and record any future drift in the overlay manifest plus the audit docs/tests.

### 3. Stage Art, Fonts, and Shaders
- Validate the entire `ui/assets` hierarchy against the retail install instead of repackaging it into a repo-owned runtime bundle. This includes HUD chrome, score state textures, menu backgrounds, and national flags.
- Point the font bake step at `assets/quakelive/baseq3/fonts/` so the canonical Quake Live TTFs (`handelgothic.ttf`, `notosans-regular.ttf`, `droidsansmono.ttf`, `droidsansfallbackfull.ttf`) remain intact in their original location. Treat this directory as the staging input for packaging rather than copying the binaries elsewhere.
- Run the font bake tool (`tools/packaging/bake_fonts.py`, invoked automatically by `tools/build_ui_bundle.sh`) against the staged TTFs to regenerate `fonts/font`, `fonts/smallfont`, `fonts/bigfont`, and `fonts/monofont` atlases that match scripted `textscale` expectations. When the FreeType Python bindings are available (`python3 -m pip install freetype-py`), the tool rasterizes each TTF into `.tga` atlases during the build. When FreeType is unavailable, the tool still emits deterministic `.dat` metadata, placeholder `.tga` atlas files, and the expected metrics payload so CI/bundle generation can proceed without blocking on an external wheel. `handelgothic.ttf` feeds the default `font`/`bigFont` look, `notosans-regular.ttf` drives the `smallFont` text blocks, `droidsansmono.ttf` is used for mono UI widgets, and `droidsansfallbackfull.ttf` keeps multilingual glyphs available for HUD prompts. Metrics for every bake land in `artifacts/ui_bundle/metrics/font_metrics.json` so CI can spot glyph drift.
- **License handling:** Handel Gothic is proprietary; only use the TTF and generated atlases for Quake Live compatibility testing, and avoid redistributing those artifacts outside the local build output. Droid Sans and Noto Sans remain under Apache 2.0.
- Bring over the `ui*.shader` files and any dependent materials so gradients, cursors, and overlay effects compile correctly.

### 4. Prepare Validation Inputs
- Keep the validation recipe under version control (for example `tools/build_ui_bundle.sh`, which now runs the retail corpus check, records the drift manifest, removes stale duplicate-package artifacts, and bakes font metrics without writing a retail UI PK3 by default).
- The preflight now runs `scripts/ui/check_retail_ui_corpus.py --strict` first, so missing retail configs, fonts, shaders, menus, icons, and levelshots are reported together before validation starts.
- Hosted CI runs that same preflight before strict bundle generation. If the proprietary retail corpus is not staged on the runner, CI uploads the missing-input inventory and a non-enforced parity-gate report, then skips the bundle/font/headless validation path that requires those undistributable inputs.
- `artifacts/ui_bundle/ui_src_retail_overlay.json` records the drift policy, the deterministic hash and size for every drifted file, and stale-file cleanup evidence so CI can verify that duplicate retail overrides are not being materialized by default.
- `artifacts/ui_bundle/runtime_ui_package_manifest.json` is written only for explicit `--runtime-root` refreshes. It records the runtime root, package hashes, required-entry coverage, and the exact overlay-entry list so local probe automation can fail fast before launch.
- Track validation manifests under `tools/` so the retail-input recipe is auditable. `tools/packaging/ui_bundle_manifest.json` now lists the Quake Live font binaries sourced from `assets/quakelive/baseq3/fonts/`, their HUD roles (`font`, `smallFont`, `bigFont`, `mono`), and the license caveats (Handel Gothic remains proprietary, while the Droid and Noto families stay under Apache 2.0).

### 5. Validate In-Game
- Launch with a clean homepath to ensure stale local PK3s are not masking the retail install. `tests/run_ui_validation.py` now reads directly from the detected retail `baseq3` root while parsing representative HUD/menu panels for font references.
- The client runtime probe now performs an explicit runtime-root refresh before launch and refuses to continue unless `runtime_ui_package_manifest.json` and the required UI package entries were emitted successfully.
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
- [x] The current `src/ui` runtime-panel compare is clean (`65 / 65`, `0` content diffs), and any future drift must be captured by the overlay manifest/runtime package proof path.
- [ ] Default validation runs leave retail runtime PK3s unmaterialized, while explicit runtime-refresh/probe flows emit reproducible PK3s plus `runtime_ui_package_manifest.json` when the writable homepath contract needs them.
- [ ] `tools/build_ui_bundle.sh` completes without error and `python tests/run_ui_validation.py` reports no glyph/shader drift.
- [ ] `python -B -m pytest tests/test_ui_full_parity_gate.py -q` writes `artifacts/ui_validation/logs/ui_full_parity_gate.json` and any non-passing tranche is understood before landing changes.
- [ ] Accessibility guidelines (redundant cues, locale support, typography) are verified during manual QA.
- [ ] Documentation and commit messages capture any deviations from Quake Live defaults or new accessibility accommodations.
