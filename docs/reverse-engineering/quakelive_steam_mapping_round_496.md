# Quake Live Steam Mapping Round 496: GameServer Init Signature and Cold Failure State

## Scope

This round tightens the Steam GameServer launch/runtime boundary around the
retail `SteamGameServer_Init(...)` call. The focus is the exact init signature,
the success/failure state transition, and the source fallback behavior when
Steam's GameServer entry point fails.

Retail Quake Live treats GameServer init failure as fatal. SRP intentionally
keeps live online services behind `QL_BUILD_ONLINE_SERVICES` and uses a
compatibility fallback instead, so the important reconstructed contract is:
failed init must not mark the GameServer path initialized, must not run the
GameServer callback pump, and must not switch workshop calls onto the
GameServer UGC owner.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/common/platform/platform_steamworks.c`
- `tests/steamworks_harness.c`
- `tests/test_platform_services.py`
- `tests/test_steamworks_harness.py`

Observed facts:

- Ghidra imports record `STEAM_API.DLL!SteamGameServer_Init @ 00159314`.
- Retail HLIL at `sub_466DB0` / the surrounding bootstrap calls
  `SteamGameServer_Init` with Steam port `0`, the configured game port, query
  port `0xffff`, secure mode `sv_vac + 2`, and the retained version string.
- Retail stores the returned value into `data_e30358` immediately after the
  call.
- Retail checks the stored value and calls the fatal error path when the
  result is zero.
- SRP mirrors the call signature but converts the failure into a disabled
  compatibility state instead of a fatal exit, in line with the repository's
  online-services containment rule.

## Reconstruction

Implemented mapping and test changes:

- Exposed the already-recorded Steam port and query port from the Steamworks
  harness so Python tests can assert the complete retail init signature.
- Strengthened `test_game_server_init_uses_retail_init_signature_and_dedicated_ugc_owner`
  to assert Steam port `0`, query port `0xffff`, secure/no-auth modes, retained
  version strings, and repeated-init no-reentry.
- Added a failure-state harness regression proving that a failed
  `SteamGameServer_Init` call:
  - records the same retail init signature,
  - leaves `QL_Steamworks_ServerIsInitialised()` false,
  - does not run `SteamGameServer_RunCallbacks()`,
  - does not route UGC calls through `SteamGameServerUGC`, and
  - does not call `SteamGameServer_Shutdown()`.
- Added static source/HLIL parity assertions for the import, the retail init
  call, the stored init result, the failure branch, and SRP's source guard
  ordering before `state.gameServerInitialised = qtrue`.

No live Steam services were enabled, and no production Steam behavior was moved
outside the existing `QL_BUILD_ONLINE_SERVICES` containment.

## Validation

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_game_server_init_uses_retail_init_signature_and_dedicated_ugc_owner tests/test_steamworks_harness.py::test_game_server_init_failure_keeps_server_runtime_state_cold -q --tb=short`
  - 4 passed across disabled and enabled Steamworks harness builds.
- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - 124 passed.
- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots tests/test_platform_services.py::test_server_init_reconstructs_retail_hostname_and_bootstrap_metadata -q --tb=short`
  - 2 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. The retail HLIL/static source checks and harness
coverage answer this mapping question without needing a runtime client/server
process.

## Confidence

High confidence for the GameServer init signature and cold-failure state:

- Import table, HLIL call arguments, source call site, harness-recorded
  arguments, and executable failure behavior now agree.

Medium confidence for the exact retail fatal-owner name:

- The fatal failure call is anchored by HLIL address and message prefix, but
  this pass does not promote a new symbol for the retail error helper.

## Parity Estimate

Focused Steam GameServer init signature and failure-state mapping:

- Before: 86%
- After: 98%

Overall Steam launch/runtime integration:

- Before: 89.7%
- After: 89.8%
