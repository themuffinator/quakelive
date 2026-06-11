# Quake Live Steam Mapping Round 493: GameServer Shutdown Callback Boundary

## Scope

This round hardens the Steam GameServer shutdown owner boundary. Retail
`sub_465D30` is intentionally narrow: when the retained GameServer initialized
flag is set, it calls `SteamGameServer_Shutdown()` and clears that flag. It does
not tear down the `SteamServerCallbacks` bundle from this direct shutdown
helper.

SRP already matched that boundary in source. This pass adds explicit static and
executable guardrails so future cleanup work does not merge direct GameServer
runtime shutdown with callback-bundle destruction. Full platform shutdown still
owns server callback unregistration before cascading into GameServer shutdown.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `src/common/platform/platform_steamworks.c`
- `tests/test_platform_services.py`
- `tests/test_steamworks_harness.py`

Observed facts:

- `functions.csv` records `FUN_00465d30` at `0x00465D30`, size `26`, for the
  direct retail GameServer shutdown helper.
- Ghidra imports record `STEAM_API.DLL!SteamGameServer_Shutdown`.
- Retail `0x00465D30` checks `data_e30358 != 0`, calls
  `SteamGameServer_Shutdown()`, and clears `data_e30358 = 0`.
- The retail `0x00465D30..0x00465D50` body does not call
  `SteamAPI_UnregisterCallback`.
- `functions.csv` records `FUN_00466db0` at `0x00466DB0`, size `272`, for the
  `SteamServerCallbacks` registration constructor.
- `analysis_symbols.txt` promotes the imported `SteamServerCallbacks`
  `CCallback` vtables and RTTI, keeping callback-bundle ownership separate from
  the narrow GameServer shutdown helper.

## Source Mapping

No production C source behavior changed in this pass.

Hardened mapping/test coverage:

- Extended static platform-service parity coverage with:
  - the `FUN_00465d30` and `FUN_00466db0` Ghidra function anchors,
  - the `SteamGameServer_Shutdown` import anchor,
  - an HLIL slice proving the direct retail shutdown helper calls
    `SteamGameServer_Shutdown()` before clearing the initialized flag,
  - an assertion that the retail shutdown slice does not contain
    `SteamAPI_UnregisterCallback`,
  - source assertions that `QL_Steamworks_ServerShutdown` preserves that same
    narrow boundary.
- Added Steamworks harness coverage proving direct
  `QL_Steamworks_ServerShutdown` does not unregister registered server callback
  objects.
- Extended full `QL_Steamworks_Shutdown` harness coverage so platform shutdown
  is the owner that unregisters server callbacks before cascading to
  GameServer shutdown.

This keeps the default disabled-online-services policy unchanged.

## Validation

Focused validation passed:

- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_steamworks_harness.py::test_game_server_shutdown_preserves_retail_callback_owner_boundary tests/test_steamworks_harness.py::test_shutdown_cascades_game_server_shutdown -q --tb=short`
  - 4 passed across disabled and enabled Steamworks harness builds.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. The question was settled by committed retail
references, focused source assertions, harness coverage, and the normal engine
build.

## Confidence

High confidence for the direct GameServer shutdown owner:

- HLIL, Ghidra function metadata, import evidence, and source/harness behavior
  all agree that direct server shutdown only owns the GameServer runtime flag
  and `SteamGameServer_Shutdown` call.

Medium confidence for retail lifetime of the heap-allocated callback bundle:

- Retail clearly allocates and registers `SteamServerCallbacks`, but the
  committed evidence used in this pass does not show the final object
  destruction path. SRP keeps explicit callback unregistration under full
  platform shutdown as a safer compatibility cleanup while preserving the
  direct shutdown helper boundary.

## Parity Estimate

Focused GameServer shutdown callback-boundary mapping:

- Before: 88%
- After: 98%

Overall Steam launch/runtime integration:

- Before: 89.3%
- After: 89.4%
