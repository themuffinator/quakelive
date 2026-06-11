# Quake Live Steam Mapping Round 494: Callback GameServer Flag and Pump Split

## Scope

This round reconstructs the Steam callback owner flag that separates normal
client callbacks from GameServer callbacks. Retail Quake Live uses distinct
runtime pumps: `SteamAPI_RunCallbacks()` for client-side callbacks and
`SteamGameServer_RunCallbacks()` for GameServer callbacks. The
`SteamServerCallbacks` objects also retain callback flag `0x02` before they are
registered with Steam.

The source now preserves that flag for SRP server callback objects and the
Steamworks harness now models the same split when dispatching queued mock
callbacks.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/common/platform/platform_steamworks.c`
- `tests/steamworks_harness.c`
- `tests/test_platform_services.py`
- `tests/test_steamworks_harness.py`

Observed facts:

- Retail client callback pumping at `sub_461D40` checks the retained Steam
  client-initialized flag and calls `SteamAPI_RunCallbacks()`.
- Retail GameServer frame pumping at `sub_466850` checks the retained
  GameServer-initialized flag and calls `SteamGameServer_RunCallbacks()`.
- Retail `SteamServerCallbacks` construction at `sub_466DB0` writes the
  callback flags byte to `2` before each `SteamAPI_RegisterCallback` call in
  the server callback bundle.
- The server callback constructor registers callback IDs `0x65`, `0x66`,
  `0x67`, `0x8f`, and `0x4b2`. The `0x4b2` P2P session request ID also exists
  in the client callback bundle, making the callback owner flag observable and
  important.
- Ghidra imports record both `SteamAPI_RunCallbacks` and
  `SteamGameServer_RunCallbacks`, as well as `SteamAPI_RegisterCallback`.

## Source Reconstruction

Implemented source-side changes:

- Added retained callback flag constants for registered callbacks and
  GameServer-owned callbacks.
- Extended `QL_Steamworks_PrepareCallbackObject` with a `gameServer` owner
  argument.
- Passed `qtrue` for every `QL_Steamworks_RegisterServerCallbacks` callback
  object and `qfalse` for client, avatar, lobby, microtransaction, workshop,
  and UGC call-result objects.
- Preserved the GameServer flag when `QL_Steamworks_RegisterCallbackObject`
  adds the local registered bit.
- Updated the Steamworks harness queue so pending callback events carry their
  client/GameServer pump owner.
- Updated harness dispatch so a client pump does not consume GameServer events
  and the GameServer pump does not consume client events.
- Added executable coverage that queues both client and server callbacks,
  intentionally runs the wrong pump first, and verifies the correct pump still
  delivers the retained event.

The change remains behind the existing Steamworks/online-services build path
and does not enable live online services in the default build.

## Validation

Focused validation passed:

- `python -m pytest tests/test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - 2 passed.
- `python -m pytest tests/test_steamworks_harness.py::test_client_and_server_callback_pumps_preserve_retail_owner_split tests/test_steamworks_harness.py::test_server_connection_and_p2p_callbacks_dispatch_from_server_callback_pump tests/test_steamworks_harness.py::test_server_gs_stats_callbacks_dispatch_from_server_callback_pump -q --tb=short`
  - 6 passed across disabled and enabled Steamworks harness builds.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - 120 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. Static retail evidence, focused source
assertions, harness coverage, and normal build validation are sufficient for
this callback-owner reconstruction.

## Confidence

High confidence for the callback-owner flag:

- HLIL shows repeated `callbackFlags = 2` writes in the retail server callback
  constructor immediately before registration.
- Source, static tests, and harness behavior now agree with the distinct client
  and GameServer callback pump model.
- The shared P2P callback ID gives executable evidence that pump ownership is
  not merely cosmetic.

Medium confidence for every historical Steam runtime edge:

- The exact internal Steam callback dispatcher is not reconstructed here; SRP
  preserves the observable object flags and public pump split shown by retail
  evidence.

## Parity Estimate

Focused Steam callback GameServer flag and pump-owner mapping:

- Before: 78%
- After: 98%

Overall Steam launch/runtime integration:

- Before: 89.4%
- After: 89.6%
