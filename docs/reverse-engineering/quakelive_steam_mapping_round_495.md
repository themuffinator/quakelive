# Quake Live Steam Mapping Round 495: Non-GameServer Callback Owner Bits

## Scope

This round maps the normal Steam callback owner bit for the callback families
that retail keeps on the `SteamAPI_RunCallbacks()` pump: client callbacks, the
Steam avatar data source callback, lobby callbacks, microtransaction
authorization, UGC call results, and workshop callbacks.

Round 494 restored the GameServer-owned side of the same contract. This pass
pins the other half: retail callback objects whose template owner parameter is
`0` keep their callback flag byte at zero before registration and must not be
consumed by `SteamGameServer_RunCallbacks()`.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/common/platform/platform_steamworks.c`
- `tests/test_platform_services.py`
- `tests/test_steamworks_harness.py`

Observed facts:

- Ghidra promoted RTTI/vtable symbols include `...,0` for the normal callback
  families: `SteamCallbacks`, `SteamDataSource`, `SteamLobbyCallbacks`,
  `SteamMicroCallbacks`, and `SteamWorkshopCallbacks`.
- Retail client callback construction at `sub_4613A0` registers
  `GameRichPresenceJoinRequested`, `UserStatsReceived`, `PersonaStateChange`,
  client `P2PSessionRequest`, `GameServerChangeRequested`, and
  `FriendRichPresenceUpdate` without writing callback flag `2`.
- Retail avatar callback construction leaves the callback flag byte zero before
  registering `AvatarImageLoaded_t` with callback ID `0x14e`.
- Retail lobby callback construction at `sub_4656A0` repeatedly leaves the
  callback flag byte zero before registering lobby callback IDs `0x201`,
  `0x1f8`, `0x1fa`, `0x1fb`, `0x1f9`, `0x1fd`, `0x200`, and `0x14d`.
- Retail microtransaction callback setup at `sub_4659E0` registers
  `MicroTxnAuthorizationResponse_t` with callback ID `0x98` after zeroing the
  callback object storage.
- Retail workshop callback construction at `sub_4696D0` leaves both workshop
  callback flag bytes zero before registering `ItemInstalled_t` (`0xd4d`) and
  `DownloadItemResult_t` (`0xd4e`).

## Source Reconstruction

No production source change was required in this pass. The current
`QL_Steamworks_PrepareCallbackObject` call sites already pass `qfalse` for
client, UGC call-result, avatar, lobby, microtransaction, and workshop callback
objects, preserving the retail non-GameServer owner bit.

Implemented mapping and test changes:

- Added static parity checks that every non-server callback bundle passes
  `qfalse` into `QL_Steamworks_PrepareCallbackObject`.
- Added Ghidra symbol checks for the `...,0` callback vtables across all
  non-server callback families.
- Added HLIL anchors for the client, avatar, lobby, microtransaction, and
  workshop callback constructors showing zero owner bytes and matching
  `SteamAPI_RegisterCallback` IDs.
- Added a harness regression that queues rich presence, lobby creation,
  microtransaction authorization, and workshop install callbacks, then runs
  `SteamGameServer_RunCallbacks()` first and verifies none are consumed until
  the client callback pump runs.

The pass stays within the existing Steamworks/online-services containment:
live Steam services remain behind `QL_BUILD_ONLINE_SERVICES`, default disabled.

## Validation

Focused validation passed:

- `python -m pytest tests/test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_steamworks_harness.py::test_non_server_callback_bundles_survive_gameserver_callback_pump tests/test_steamworks_harness.py::test_client_and_server_callback_pumps_preserve_retail_owner_split -q --tb=short`
  - 4 passed across disabled and enabled Steamworks harness builds.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - 122 passed.
- `python -m pytest tests/test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - 2 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. Static retail evidence and the focused harness
pump-owner regression are sufficient for this callback-owner mapping pass.

## Confidence

High confidence for the non-GameServer callback owner mapping:

- Ghidra symbol names, HLIL byte-field writes, callback IDs, source call-site
  owner arguments, and executable harness behavior agree.
- The harness intentionally exercises the wrong pump first, which makes the
  owner split observable rather than merely structural.

Medium confidence for untouched Steam launch/runtime edges:

- This round does not reconstruct new Steam startup, auth, overlay, workshop
  download, or GameServer state transitions. It narrows the callback-pump
  ownership model that those runtime paths depend on.

## Parity Estimate

Focused non-GameServer callback owner-bit mapping:

- Before: 84%
- After: 98%

Overall Steam launch/runtime integration:

- Before: 89.6%
- After: 89.7%
