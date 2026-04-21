# Quake Live Asset & Config Audit

> Working asset inventory with historical sections. The current repo-wide gap
> register lives in `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`.
> Notes below about early missing pipeline work should be read in that context;
> later native-build and overlay work closed part of the original gap.

## HUD and Menu Asset Inventory

| Category | Reference Snapshot (present under `assets/quakelive/baseq3/`) | GPL Tree Coverage | Notes |
| --- | --- | --- | --- |
| Menu definitions | `.menu` and `.txt` files for competitive HUDs, scoreboards, ingame flows, intro, and front-end menus (for example `ui/comp_hud.menu`, `ui/end_scoreboard_duel.menu`, `ui/main.menu`).【68ce2a†L154-L208】 | Bundled into the staged UI package via `tools/packaging/ui_bundle_manifest.json` so the full `baseq3/ui/` tree is now copied into `build/ui_bundle/staging/ui/`. | The packaged `ui/*.menu` and `.txt` set restores Quake Live menu coverage without touching the read-only `src/ui/` tree. |
| HUD shaders & materials | `scripts/ui.shader`, `scripts/ui_hud.shader`, and supporting shader script files.【68ce2a†L121-L152】 | No Quake Live-specific shader scripts reside in the source tree; only legacy shader assets referenced in the GPL release are available. | Shader packages must be generated from the reference `.shader` files and distributed with the new UI menus. |
| Fonts | Droid Sans, Noto Sans, Handel Gothic font assets used by the Quake Live HUD (`fonts/*.ttf`).【68ce2a†L103-L120】 | Canonical TTFs continue to live under `assets/quakelive/baseq3/fonts/` so the original filenames (`handelgothic.ttf`, `notosans-regular.ttf`, `droidsansmono.ttf`, `droidsansfallbackfull.ttf`) stay intact. | `font`/`bigFont` pulls from Handel Gothic, `smallFont` text blocks come from Noto Sans, `mono` widgets use Droid Sans Mono, and multilingual fallbacks rely on Droid Sans Fallback. Package the TTFs alongside regenerated atlases and respect the licenses (Handel Gothic remains proprietary, while Droid/Noto stay under Apache 2.0). |
| Icons & levelshots | Gameplay icons, rune art, ammo, and levelshot JPEGs are preserved in the snapshot (`icons/*.png`, `levelshots/*.jpg`).【68ce2a†L27-L102】 | Not stored directly under `src/`, but the current UI bundle pipeline stages the retail `icons/` and `levelshots/` trees from the reference snapshot into the packaged output. | Runtime package proof now covers this staged payload; the remaining work here is runtime screenshot/launch QA, not basic asset availability. |
| UI binary modules | `uix86.dll` and supporting VM binaries live in the reference tree.【68ce2a†L209-L214】 | GPL tree offers C sources in `src/code/ui/` plus the current native project files and validation docs under `src/code/*.vcxproj`, `docs/build-pipeline.md`, and `docs/windows-native-pipeline.md`. | The remaining gap is reliable retail-compatible build/runtime validation and packaging, not the absence of a native DLL pipeline. |

## UI Asset Audit (Retail Snapshot vs `src/ui`)

This inventory compares the retail capture under `assets/quakelive/baseq3/ui` against the
read-only checked-in `src/ui` runtime-panel set. The goal is to separate the
current script/menu parity state from the distinct bundle/runtime path that
supplies retail art, fonts, icons, and levelshots.

### `src/ui` Inventory State

| Retail capture evidence | Current `src/ui` state | Notes |
| --- | --- | --- |
| The retail UI runtime corpus exposes 65 `.menu` / `.txt` files that drive the main menu, HUD presets, scoreboards, spectator overlays, and in-game panels. | `src/ui` now carries the same 65 runtime panel files, and the current compare is clean: `65 / 65`, `0` missing, `0` extra, `0` content diffs. | `artifacts/ui_bundle/ui_src_retail_overlay.json` now records `drift_files: []`, so the overlay path is a regression sentinel instead of an active correction path. |
| The retail UI VM loads cursor, gradient bar, scoreboard chrome, flags, and other art from `ui/assets/*` during initialization (e.g., `ui/assets/gradientbar2.tga`, `ui/assets/scrollbar.tga`, `ui/assets/slider2.tga`).【F:references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt†L2327-L2367】 | `src/ui` intentionally remains a script/header tree and does not mirror the 454-file retail `ui/assets/` subtree. | Retail art parity is supplied by `tools/build_ui_bundle.py`, which stages the snapshot into `build/ui_bundle/staging/ui/assets/` and `pak_uiql.pk3` for runtime probes. |
| Local runtime probes need packaged `ui/*.menu`, `ui/*.txt`, `ui/assets/*`, fonts, icons, and levelshots under a writable `baseq3`. | The runtime package manifest now records `pak_uiql.pk3` plus a bounded overlay slot that remains unmaterialized when `drift_files` is empty. | Explicit `--runtime-root` refreshes prove the package contract without requiring a duplicated overlay package on clean worktrees. |

### Font Coverage Notes

The retail HUD scripts expect baked font atlases (`fonts/font`, `fonts/smallfont`, `fonts/bigfont`) defined in the competitive HUD asset globals.【F:assets/quakelive/baseq3/ui/hud3.menu†L7-L24】 The UI bundle manifest shows the Quake Live TTF sources that are required to generate these atlases (Handel Gothic, Noto Sans, Droid Sans Mono, and Droid Sans Fallback).【F:tools/packaging/ui_bundle_manifest.json†L1-L78】 Ensure the font bake step runs so the atlas files exist alongside the menu scripts; otherwise the HUD falls back to legacy fonts.

### Runtime Panel Drift Status

The current checked-in runtime panel set is exact at `65 / 65` files with `0`
content diffs against the staged retail corpus. Earlier spectator-menu, join-panel,
and merge-conflicted HUD text divergences are no longer active on the current
worktree.

`src/ui/menudef.h` remains a source-side helper header rather than part of the
runtime panel corpus used by the UI parity gates. Retail HUD/menu art similarly
comes from the staged bundle path, not from a checked-in `src/ui/assets/`
mirror.

The writable correction path in `scripts/ui/write_retail_ui_overrides.py`
remains available for future regression triage, but the current overlay
manifest and runtime package manifest both report an empty `drift_files` list,
so `pak_ui_src_retail_overlay.pk3` is optional and typically absent on a clean
runtime refresh.

## Configuration Defaults

The Quake Live snapshot captures the full `default.cfg` bindings, movement, and chat shortcuts used by the retail client.【fcaf97†L1-L86】 The GPL tree still carries Quake III defaults that diverge in multiple areas (weapon toggle, drop bindings, vote commands). Engine startup routines (`Cbuf_AddText("exec default.cfg\n")`) assume a `default.cfg` is shipped alongside the data packages.【F:src/code/qcommon/common.c†L2389-L2405】【F:src/code/ui/ui_main.c†L3223-L3263】 Aligning with Quake Live therefore requires copying the reference `default.cfg` (and curated class configs such as `tim.cfg`/`syncerror.cfg`).【68ce2a†L215-L224】 Documentation must highlight the new bindings so downstream projects can update migration guides.

## Platform DLL Dependencies

The reference dump enumerates the Windows launcher (`quakelive_steam.exe`) and supporting DLLs for Chromium/Awesomium UI, FFmpeg codecs, Steam integration, and XInput.【ed6b1b†L1-L13】 Notably absent are the Visual C++ runtime redistributables (`MSVCR100.dll`, `MSVCP100.dll`) that the binary imports, implying they were provided by the system installer rather than bundled locally.【docs/build-pipeline.md†L20-L33】 Linux server shared objects (`qagamei386.so`, `qagamex64.so`) are preserved under `baseq3/` for parity testing.【68ce2a†L149-L214】 Any packaging workflow must account for these external dependencies or replace them with open-source equivalents when targeting new platforms.

## Packaging & Regeneration Process

1. **Extract Quake Live UI assets** – Use `tools/build_ui_bundle.sh` (via the manifest) to copy `baseq3/ui/*.menu` and `baseq3/ui/*.txt` into `build/ui_bundle/staging/ui/`. Maintain directory layout to satisfy `trap_FS_FOpenFile` lookups.
   - The default build flow keeps retail runtime PK3s unmaterialized and records the current drift contract in `artifacts/ui_bundle/ui_src_retail_overlay.json`; on the clean worktree that contract is empty.
   - When a local runtime probe needs writable-homepath packages, call `tools/build_ui_bundle.py --runtime-root <baseq3>` to emit `pak_uiql.pk3`, emit `pak_ui_src_retail_overlay.pk3` only if drift reappears, and always write `artifacts/ui_bundle/runtime_ui_package_manifest.json`.
2. **Compile UI code** – Extend the native build pipeline described in `docs/build-pipeline.md` to emit `uix86.dll`, linking against the VS2010 runtime to mirror import tables.【docs/build-pipeline.md†L20-L34】 Place the binary next to the staged UI scripts so clients can load the native module.
3. **Prepare shader and font resources** – Copy `scripts/ui*.shader` into `baseq3/scripts/` and run the Quake III font generator (or an equivalent freetype-based tool) against the TTFs stored under `assets/quakelive/baseq3/fonts/` to produce `.tga` atlases referenced by the menus. Record the generator inputs so future HUD changes can be rebuilt reproducibly and call out the source/license for each TTF (Handel Gothic is redistribution-restricted, Droid/Noto are Apache 2.0).
4. **Bundle art dependencies** – Stage icons and levelshots used by the menus under `baseq3/icons/` and `baseq3/levelshots/`, and keep the full retail `ui/assets/` tree mounted beside the menu scripts. The renderer already accepts PNG/JPG/TGA via the `tr_image.c` load path, so keep the snapshot PNG/JPEG assets unless a downstream toolchain requires TGA conversion.
5. **Assemble distributable packages** – For local runtime probes, use the explicit `--runtime-root` path to zip the staged directories into `pak_uiql.pk3`, emit the bounded overlay PK3 only when `drift_files` is non-empty, and verify the result through `runtime_ui_package_manifest.json`. Ensure `default.cfg` and curated configs live at the root of the main PK3 so the engine bootstrap succeeds, and honor the packaging manifest at `tools/packaging/ui_bundle_manifest.json` so the reference fonts are copied from `assets/quakelive/baseq3/fonts/` into `fonts/*.ttf` for `FS_InitFilesystem` checks.
6. **Verify bootstrap diagnostics** – The filesystem now emits preflight warnings enumerating which search path (homepath/basepath/cdpath) was missing `default.cfg`, key `ui/*.menu` scripts, or the required TTFs. Use these logs to confirm your PK3 layout matches the expected Quake Live directory tree before distributing builds.
7. **Document regeneration commands** – Add scripts (PowerShell/Bash) that call out the exact copy, conversion, and `zip` commands, allowing automated rebuilds when upstream assets change. Reference this document from README/porting guides so contributors can rerun the pipeline.

### Packaging command sequence

Run the UI bundle pipeline from the repository root to stage the HUD assets, validate the manifest, and emit a distributable PK3:

```bash
export REPO_ROOT="$(git rev-parse --show-toplevel)"
bash tools/build_ui_bundle.sh
```

The script copies `default.cfg`, the Quake Live TTF set (`fonts/*.ttf`), shader scripts (`scripts/ui*.shader`), the full retail `ui/assets/` tree, gameplay `icons/`, `levelshots/`, and the entire `ui/*.menu`/`ui/*.txt` tree into `build/ui_bundle/staging/`. By default it leaves retail runtime PK3s unmaterialized and writes the overlay/report artifacts instead; on the clean worktree those artifacts record an empty drift contract. When a probe needs writable-homepath packages, run `python tools/build_ui_bundle.py --runtime-root build/win32/Debug/bin/baseq3` to emit `pak_uiql.pk3`, emit `pak_ui_src_retail_overlay.pk3` only if drift reappears, and write `artifacts/ui_bundle/runtime_ui_package_manifest.json`. The build enforces the manifest-defined audit gates before packaging. When `freetype-py` is unavailable, the font bake step falls back to deterministic metrics plus placeholder atlas files so the bundle still completes.

## Configuration Alignment Plan

1. **Adopt Quake Live defaults** – Promote `assets/quakelive/baseq3/default.cfg` to the active data set so new builds ship with Quake Live bindings. Mirror any class configs required for tutorials (`tim.cfg`, `sponge.cfg`, etc.).【68ce2a†L215-L224】
2. **Update documentation** – Append a controls section to `docs/repo-overview.md` (or a dedicated controls guide) summarizing the Quake Live bindings (weapon toggle on `F`, drop keys, vote shortcuts) so porting teams understand the behavioural delta from Quake III.【fcaf97†L1-L86】
3. **Validate engine expectations** – Confirm `default.cfg` is packaged into whatever PK3 the engine boots with; the existing fatal error path in `FS_ReadFile("default.cfg")` must never trigger in clean installs.【F:src/code/qcommon/files.c†L3260-L3314】 Automate this with a smoke test that launches the executable with an empty homepath and verifies startup.
4. **Surface binding diffs in migration guides** – Update `docs/porting_plan.md` or related guidance with a subsection referencing this audit so gameplay contributors align cvar defaults and UI prompts with the Quake Live baseline.

Following these steps will let future code changes consume Quake Live-flavoured assets without manual repackaging, while keeping configuration defaults consistent with the retail snapshots.
