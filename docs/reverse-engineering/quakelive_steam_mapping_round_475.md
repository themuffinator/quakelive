# Quake Live Steam Mapping Round 475: GameServer Bootstrap Success Log

## Scope

This round reconstructs the terminal success diagnostic in the dedicated
Steam GameServer bootstrap sequence. The focused source delta is intentionally
small: preserve the existing opt-in Steamworks guard while matching retail's
post-product/post-gamedir success log.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/qcommon/common.c`

Observed facts:

- The alias map promotes `sub_466ED0` to `SteamServer_Init`.
- Retail `sub_466ED0` calls the Steam GameServer product setter with
  `"Quake Live"` at `00467090`.
- Retail `sub_466ED0` calls the Steam GameServer gamedir setter with
  `"baseq3"` at `004670a0`.
- Retail then prints `Steam Gameserver initialized.` at `004670a7`.

## Source Reconstruction

Implemented source-side changes:

- Added `Com_Printf( "Steam Gameserver initialized.\n" );` after
  `QL_Steamworks_ServerSetProduct( QL_PRODUCT_NAME );` and
  `QL_Steamworks_ServerSetGameDir( QL_BASEGAME );` in
  `Com_InitSteamGameServer()`.
- Extended `tests/test_platform_services.py` to pin the HLIL product setter,
  gamedir setter, and terminal success diagnostic.
- Extended `tests/test_netcode_parity_manifest.py` to enforce the source order:
  product publication, gamedir publication, then the success log.

The live Steamworks path remains compiled only behind `QL_BUILD_STEAMWORKS`,
which is itself nested inside the repository's opt-in online-services build
policy.

## Confidence

High confidence:

- Function ownership through the alias map.
- Literal product and gamedir strings.
- Terminal success diagnostic text and ordering relative to the product and
  gamedir setters.

Open questions:

- This round does not claim full retail parity for the surrounding Steam launch
  ownership, app restart, encrypted app ticket, or client/server callback
  surfaces. Those remain covered by adjacent mapping rounds and follow-up work.

## Validation

- `python -m pytest tests/test_platform_services.py::test_server_init_reconstructs_retail_hostname_and_bootstrap_metadata tests/test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
  - 2 passed.
- `python -m pytest tests/test_platform_services.py tests/test_netcode_parity_manifest.py tests/test_steamworks_harness.py -q --tb=short`
  - 289 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.
- `dumpbin /dependents build\win32\Debug\bin\quakelive_steam.exe`
  - No dynamic `steam_api`, `libpng`, `vorbis`, or `ogg` dependency was present.
- `git diff --check -- src/code/qcommon/common.c tests/test_platform_services.py tests/test_netcode_parity_manifest.py IMPLEMENTATION_PLAN.md docs/reverse-engineering/quakelive_steam_mapping_round_475.md`
  - Passed; Git reported only LF-to-CRLF working-copy normalization warnings.

No runtime launch was needed. This pass was deterministic source
reconstruction and regression coverage from committed HLIL/Ghidra evidence.

## Parity Estimate

- Focused Steam GameServer bootstrap terminal diagnostic parity: 86% -> 99%.
- Steam launch/runtime integration parity: 81% -> 82%.
