# Quake Live Asset & Config Audit

## HUD and Menu Asset Inventory

| Category | Reference Snapshot (present under `references/original-assets/quakelive/baseq3/`) | GPL Tree Coverage | Notes |
| --- | --- | --- | --- |
| Menu definitions | `.menu` and `.txt` files for competitive HUDs, scoreboards, ingame flows, intro, and front-end menus (for example `ui/comp_hud.menu`, `ui/end_scoreboard_duel.menu`, `ui/main.menu`).【68ce2a†L154-L208】 | `src/ui/` only carries legacy Quake III scripts (`hud.txt`, `hud2.txt`, `ingame.txt`, `menus.txt`) and the shared header.【b800fb†L1-L6】 | High-fidelity Quake Live UI requires importing the full `ui/*.menu` and `.txt` set. |
| HUD shaders & materials | `scripts/ui.shader`, `scripts/ui_hud.shader`, and supporting shader script files.【68ce2a†L121-L152】 | No Quake Live-specific shader scripts reside in the source tree; only legacy shader assets referenced in the GPL release are available. | Shader packages must be generated from the reference `.shader` files and distributed with the new UI menus. |
| Fonts | Droid Sans, Noto Sans, Handel Gothic font assets used by the Quake Live HUD (`fonts/*.ttf`).【68ce2a†L103-L120】 | Fonts are absent from the GPL tree; existing builds rely on the original Quake III font images generated at build time. | Packaging requires bundling the TTFs plus regenerated font image atlases for the renderer. |
| Icons & levelshots | Gameplay icons, rune art, ammo, and levelshot JPEGs are preserved in the snapshot (`icons/*.png`, `levelshots/*.jpg`).【68ce2a†L27-L102】 | Not present under `src/` because the GPL release depends on `.pk3` packages built from Q3 art. | Bulk art import or on-demand regeneration is required to surface Quake Live visuals. |
| UI binary modules | `uix86.dll` and supporting VM binaries live in the reference tree.【68ce2a†L209-L214】 | GPL tree offers C sources in `src/code/ui/` but no native DLL build pipeline yet.【docs/reference-index.md†L9-L21】 | A native build step must output Quake Live-compatible DLLs once the asset pipeline is in place. |

## Configuration Defaults

The Quake Live snapshot captures the full `default.cfg` bindings, movement, and chat shortcuts used by the retail client.【fcaf97†L1-L86】 The GPL tree still carries Quake III defaults that diverge in multiple areas (weapon toggle, drop bindings, vote commands). Engine startup routines (`Cbuf_AddText("exec default.cfg\n")`) assume a `default.cfg` is shipped alongside the data packages.【F:src/code/qcommon/common.c†L2389-L2405】【F:src/code/ui/ui_main.c†L3223-L3263】 Aligning with Quake Live therefore requires copying the reference `default.cfg` (and curated class configs such as `tim.cfg`/`syncerror.cfg`).【68ce2a†L215-L224】 Documentation must highlight the new bindings so downstream projects can update migration guides.

## Platform DLL Dependencies

The reference dump enumerates the Windows launcher (`quakelive_steam.exe`) and supporting DLLs for Chromium/Awesomium UI, FFmpeg codecs, Steam integration, and XInput.【ed6b1b†L1-L13】 Notably absent are the Visual C++ runtime redistributables (`MSVCR100.dll`, `MSVCP100.dll`) that the binary imports, implying they were provided by the system installer rather than bundled locally.【docs/build-pipeline.md†L20-L33】 Linux server shared objects (`qagamei386.so`, `qagamex64.so`) are preserved under `baseq3/` for parity testing.【68ce2a†L149-L214】 Any packaging workflow must account for these external dependencies or replace them with open-source equivalents when targeting new platforms.

## Packaging & Regeneration Process

1. **Extract Quake Live UI assets** – Copy `baseq3/ui/*.menu`, HUD text files, and `teaminfo.txt` into a staging directory (for example `build/assets/ui/`). Maintain directory layout to satisfy `trap_FS_FOpenFile` lookups.
2. **Compile UI code** – Extend the native build pipeline described in `docs/build-pipeline.md` to emit `uix86.dll`, linking against the VS2010 runtime to mirror import tables.【docs/build-pipeline.md†L20-L34】 Place the binary next to the staged UI scripts so clients can load the native module.
3. **Prepare shader and font resources** – Copy `scripts/ui*.shader` into `baseq3/scripts/` and run the Quake III font generator (or an equivalent freetype-based tool) against the Droid/Noto fonts to produce `.tga` atlases referenced by the menus. Record the generator inputs so future HUD changes can be rebuilt reproducibly.
4. **Bundle art dependencies** – Stage icons and levelshots used by the menus under `baseq3/icons/` and `baseq3/levelshots/`. When possible, convert PNG→TGA to match renderer expectations, otherwise confirm PNG loading paths.
5. **Assemble distributable packages** – Zip the staged directories into PK3 archives (e.g., `pak100ql.pk3`) or embed them in a platform-specific installer. Ensure `default.cfg` and curated configs live at the root of the PK3 so the engine bootstrap succeeds.
6. **Document regeneration commands** – Add scripts (PowerShell/Bash) that call out the exact copy, conversion, and `zip` commands, allowing automated rebuilds when upstream assets change. Reference this document from README/porting guides so contributors can rerun the pipeline.

## Configuration Alignment Plan

1. **Adopt Quake Live defaults** – Promote `references/original-assets/quakelive/baseq3/default.cfg` to the active data set so new builds ship with Quake Live bindings. Mirror any class configs required for tutorials (`tim.cfg`, `sponge.cfg`, etc.).【68ce2a†L215-L224】
2. **Update documentation** – Append a controls section to `docs/repo-overview.md` (or a dedicated controls guide) summarizing the Quake Live bindings (weapon toggle on `F`, drop keys, vote shortcuts) so porting teams understand the behavioural delta from Quake III.【fcaf97†L1-L86】
3. **Validate engine expectations** – Confirm `default.cfg` is packaged into whatever PK3 the engine boots with; the existing fatal error path in `FS_ReadFile("default.cfg")` must never trigger in clean installs.【F:src/code/qcommon/files.c†L3260-L3314】 Automate this with a smoke test that launches the executable with an empty homepath and verifies startup.
4. **Surface binding diffs in migration guides** – Update `docs/porting_plan.md` or related guidance with a subsection referencing this audit so gameplay contributors align cvar defaults and UI prompts with the Quake Live baseline.

Following these steps will let future code changes consume Quake Live-flavoured assets without manual repackaging, while keeping configuration defaults consistent with the retail snapshots.
