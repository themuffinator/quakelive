# Quake Live Asset & Config Audit

## HUD and Menu Asset Inventory

| Category | Reference Snapshot (present under `assets/quakelive/baseq3/`) | GPL Tree Coverage | Notes |
| --- | --- | --- | --- |
| Menu definitions | `.menu` and `.txt` files for competitive HUDs, scoreboards, ingame flows, intro, and front-end menus (for example `ui/comp_hud.menu`, `ui/end_scoreboard_duel.menu`, `ui/main.menu`).【68ce2a†L154-L208】 | `src/ui/` mirrors the retail menu stack (`ui/menus.txt` loads `default.menu`, `main.menu`, `main_options.menu`, and other Quake Live front-end scripts; `hud3.menu` defines the competitive HUD globals).【F:src/ui/menus.txt†L1-L41】【F:src/ui/hud3.menu†L1-L24】 | Core scripts are in place, but layout drift and missing art bundles remain (see audit below). |
| HUD shaders & materials | `scripts/ui.shader`, `scripts/ui_hud.shader`, and supporting shader script files.【68ce2a†L121-L152】 | No Quake Live-specific shader scripts reside in the source tree; only legacy shader assets referenced in the GPL release are available. | Shader packages must be generated from the reference `.shader` files and distributed with the new UI menus. |
| Fonts | Droid Sans, Noto Sans, Handel Gothic font assets used by the Quake Live HUD (`fonts/*.ttf`).【68ce2a†L103-L120】 | Canonical TTFs continue to live under `assets/quakelive/baseq3/fonts/` so the original filenames (`handelgothic.ttf`, `notosans-regular.ttf`, `droidsansmono.ttf`, `droidsansfallbackfull.ttf`) stay intact. | `font`/`bigFont` pulls from Handel Gothic, `smallFont` text blocks come from Noto Sans, `mono` widgets use Droid Sans Mono, and multilingual fallbacks rely on Droid Sans Fallback. Package the TTFs alongside regenerated atlases and respect the licenses (Handel Gothic remains proprietary, while Droid/Noto stay under Apache 2.0). |
| Icons & levelshots | Gameplay icons, rune art, ammo, and levelshot JPEGs are preserved in the snapshot (`icons/*.png`, `levelshots/*.jpg`).【68ce2a†L27-L102】 | Not present under `src/` because the GPL release depends on `.pk3` packages built from Q3 art. | Bulk art import or on-demand regeneration is required to surface Quake Live visuals. |
| UI binary modules | `uix86.dll` and supporting VM binaries live in the reference tree.【68ce2a†L209-L214】 | GPL tree offers C sources in `src/code/ui/` but no native DLL build pipeline yet.【docs/reference-index.md†L9-L21】 | A native build step must output Quake Live-compatible DLLs once the asset pipeline is in place. |

## UI Asset Audit (Retail Snapshot vs `src/ui`)

This inventory compares the retail capture under `assets/quakelive/baseq3/ui` against the scripts currently mirrored in `src/ui`. The goal is to identify missing art/font bundles and layout drift that would diverge from retail UI captures.

### Missing UI Art/Icon Coverage

| Retail capture evidence | Gap in repo coverage | Notes |
| --- | --- | --- |
| The retail UI VM loads cursor, gradient bar, scrollbar, and slider textures from `ui/assets/*` during initialization (e.g., `ui/assets/gradientbar2.tga`, `ui/assets/scrollbar.tga`, `ui/assets/slider2.tga`).【F:references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt†L2327-L2367】 | `src/ui/` contains only menu scripts and no `ui/assets` art payload, so these textures must come from packaged assets or the retail snapshot directory. | Without the `ui/assets` bundle, scrollbars, gradients, and cursor sprites fall back or render blank. |
| Competitive HUD menus reference scorebox and ink-fade textures under `ui/assets/score/` (e.g., `scorebox_spec.tga`, `scorebox_follow.tga`, `ink_fade_left.tga`, `ink_fade_right.tga`).【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L163-L289】 | The scorebox textures are not present in `src/ui` and must be sourced from the retail `ui/assets` tree. | Missing textures remove the visible scorebox backgrounds, reducing HUD legibility. |

### Font Coverage Notes

The retail HUD scripts expect baked font atlases (`fonts/font`, `fonts/smallfont`, `fonts/bigfont`) defined in the competitive HUD asset globals.【F:assets/quakelive/baseq3/ui/hud3.menu†L7-L24】 The UI bundle manifest shows the Quake Live TTF sources that are required to generate these atlases (Handel Gothic, Noto Sans, Droid Sans Mono, and Droid Sans Fallback).【F:tools/packaging/ui_bundle_manifest.json†L1-L78】 Ensure the font bake step runs so the atlas files exist alongside the menu scripts; otherwise the HUD falls back to legacy fonts.

### Layout & Script Drift vs Retail Snapshot

| Area | Retail snapshot (`assets/quakelive/baseq3/ui`) | `src/ui` state | Impact |
| --- | --- | --- | --- |
| Spectator comparison health panels | Uses `CG_SPEC_COMPARE_PRIMARY` / `CG_SPEC_COMPARE_SECONDARY` in `comp_spectator.menu` to draw the two-player comparison bars.【F:assets/quakelive/baseq3/ui/comp_spectator.menu†L150-L161】 | Uses `CG_1ST_PLYR_HEALTH_ARMOR` / `CG_2ND_PLYR_HEALTH_ARMOR`, diverging from retail ownerdraw IDs.【F:src/ui/comp_spectator.menu†L150-L161】 | Mismatched ownerdraw IDs change which HUD data feeds the panel; retail comparison bars may not render as intended. |
| Spectator follow highlight | Retail uses `CG_SPEC_FOLLOW_PRIMARY` / `CG_SPEC_FOLLOW_SECONDARY` for the follow badges on the scoreboxes.【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L202-L252】 | `src/ui` swaps to `CG_HEALTH_COLORIZED` with follow-specific ownerdraw flags (`CG_SHOW_IF_1ST_PLYR_FOLLOWED`, `CG_SHOW_IF_2ND_PLYR_FOLLOWED`).【F:src/ui/comp_spectator_follow.menu†L202-L254】 | The follow badges no longer map to the retail ownerdraw handlers, risking incorrect highlight behavior. |
| In-game join panel | Retail `ingame_join.menu` omits a country dropdown panel in the join pop-up.【F:assets/quakelive/baseq3/ui/ingame_join.menu†L35-L100】 | `src/ui` inserts a country label/list fed by `FEEDER_COUNTRIES`.【F:src/ui/ingame_join.menu†L35-L122】 | Layout expands beyond the retail capture and depends on a feeder ID absent in the retail `menudef.h` list.【F:src/ui/menudef.h†L70-L86】【F:assets/quakelive/baseq3/ui/menudef.h†L70-L85】 |

## Configuration Defaults

The Quake Live snapshot captures the full `default.cfg` bindings, movement, and chat shortcuts used by the retail client.【fcaf97†L1-L86】 The GPL tree still carries Quake III defaults that diverge in multiple areas (weapon toggle, drop bindings, vote commands). Engine startup routines (`Cbuf_AddText("exec default.cfg\n")`) assume a `default.cfg` is shipped alongside the data packages.【F:src/code/qcommon/common.c†L2389-L2405】【F:src/code/ui/ui_main.c†L3223-L3263】 Aligning with Quake Live therefore requires copying the reference `default.cfg` (and curated class configs such as `tim.cfg`/`syncerror.cfg`).【68ce2a†L215-L224】 Documentation must highlight the new bindings so downstream projects can update migration guides.

## Platform DLL Dependencies

The reference dump enumerates the Windows launcher (`quakelive_steam.exe`) and supporting DLLs for Chromium/Awesomium UI, FFmpeg codecs, Steam integration, and XInput.【ed6b1b†L1-L13】 Notably absent are the Visual C++ runtime redistributables (`MSVCR100.dll`, `MSVCP100.dll`) that the binary imports, implying they were provided by the system installer rather than bundled locally.【docs/build-pipeline.md†L20-L33】 Linux server shared objects (`qagamei386.so`, `qagamex64.so`) are preserved under `baseq3/` for parity testing.【68ce2a†L149-L214】 Any packaging workflow must account for these external dependencies or replace them with open-source equivalents when targeting new platforms.

## Packaging & Regeneration Process

1. **Extract Quake Live UI assets** – Copy `baseq3/ui/*.menu`, HUD text files, and `teaminfo.txt` into a staging directory (for example `build/assets/ui/`). Maintain directory layout to satisfy `trap_FS_FOpenFile` lookups.
2. **Compile UI code** – Extend the native build pipeline described in `docs/build-pipeline.md` to emit `uix86.dll`, linking against the VS2010 runtime to mirror import tables.【docs/build-pipeline.md†L20-L34】 Place the binary next to the staged UI scripts so clients can load the native module.
3. **Prepare shader and font resources** – Copy `scripts/ui*.shader` into `baseq3/scripts/` and run the Quake III font generator (or an equivalent freetype-based tool) against the TTFs stored under `assets/quakelive/baseq3/fonts/` to produce `.tga` atlases referenced by the menus. Record the generator inputs so future HUD changes can be rebuilt reproducibly and call out the source/license for each TTF (Handel Gothic is redistribution-restricted, Droid/Noto are Apache 2.0).
4. **Bundle art dependencies** – Stage icons and levelshots used by the menus under `baseq3/icons/` and `baseq3/levelshots/`. When possible, convert PNG→TGA to match renderer expectations, otherwise confirm PNG loading paths.
5. **Assemble distributable packages** – Zip the staged directories into PK3 archives (e.g., `pak100ql.pk3`) or embed them in a platform-specific installer. Ensure `default.cfg` and curated configs live at the root of the PK3 so the engine bootstrap succeeds, and honor the packaging manifest at `tools/packaging/ui_bundle_manifest.json` so the reference fonts are copied from `assets/quakelive/baseq3/fonts/` into `fonts/*.ttf` for `FS_InitFilesystem` checks.
6. **Verify bootstrap diagnostics** – The filesystem now emits preflight warnings enumerating which search path (homepath/basepath/cdpath) was missing `default.cfg`, key `ui/*.menu` scripts, or the required TTFs. Use these logs to confirm your PK3 layout matches the expected Quake Live directory tree before distributing builds.
7. **Document regeneration commands** – Add scripts (PowerShell/Bash) that call out the exact copy, conversion, and `zip` commands, allowing automated rebuilds when upstream assets change. Reference this document from README/porting guides so contributors can rerun the pipeline.

### Packaging command sequence

Run the UI bundle pipeline from the repository root to stage the HUD assets, validate the manifest, and emit a distributable PK3:

```bash
export REPO_ROOT="$(git rev-parse --show-toplevel)"
bash tools/build_ui_bundle.sh
```

The script copies `default.cfg`, the Quake Live TTF set (`fonts/*.ttf`), shader scripts (`scripts/ui*.shader`), and the entire `ui/*.menu`/`ui/*.txt` tree into `build/ui_bundle/staging/`. It then enforces the manifest-defined audit gates (required paths and globs) before invoking `zip`, causing the build to fail if any required file is missing or placed under the wrong PK3 path.

## Configuration Alignment Plan

1. **Adopt Quake Live defaults** – Promote `assets/quakelive/baseq3/default.cfg` to the active data set so new builds ship with Quake Live bindings. Mirror any class configs required for tutorials (`tim.cfg`, `sponge.cfg`, etc.).【68ce2a†L215-L224】
2. **Update documentation** – Append a controls section to `docs/repo-overview.md` (or a dedicated controls guide) summarizing the Quake Live bindings (weapon toggle on `F`, drop keys, vote shortcuts) so porting teams understand the behavioural delta from Quake III.【fcaf97†L1-L86】
3. **Validate engine expectations** – Confirm `default.cfg` is packaged into whatever PK3 the engine boots with; the existing fatal error path in `FS_ReadFile("default.cfg")` must never trigger in clean installs.【F:src/code/qcommon/files.c†L3260-L3314】 Automate this with a smoke test that launches the executable with an empty homepath and verifies startup.
4. **Surface binding diffs in migration guides** – Update `docs/porting_plan.md` or related guidance with a subsection referencing this audit so gameplay contributors align cvar defaults and UI prompts with the Quake Live baseline.

Following these steps will let future code changes consume Quake Live-flavoured assets without manual repackaging, while keeping configuration defaults consistent with the retail snapshots.
