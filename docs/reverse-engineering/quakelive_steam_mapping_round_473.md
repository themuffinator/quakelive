# Quake Live Steam Mapping Round 473: GameServer Orphaned Auth Cleanup

## Scope

This round tightens the server-spawn Steam auth cleanup lane around retail
`sub_466B90`. Earlier mapping identified the helper as
`SteamServer_EndOrphanedAuthSessions`, but the source only ended auth sessions
from individual client-drop paths.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/quakelive_steam_mapping_round_156.md`

Observed facts:

- The alias map promotes `sub_466B90` to
  `SteamServer_EndOrphanedAuthSessions`.
- Retail `SV_SpawnServer` calls `sub_466B90()` immediately after the
  `Server: %s\n` log and before `sub_4F43A0()`, the following map-loading
  owner.
- `sub_466B90` walks the retained Steam auth-session tree and compares each
  SteamID against the current server client table.
- When an auth session no longer matches a live client, retail logs the
  `Found an authed client...` diagnostic and queues that SteamID for cleanup.
- When the GameServer initialized flag is set, retail calls
  `SteamGameServer()->EndAuthSession(...)` through vtable slot `0x78`, removes
  the SteamID from the retained auth tree, and logs the
  `Called EndAuthSession...` diagnostic.
- When the GameServer initialized flag is clear, retail logs the
  `Can't end auth session...` diagnostic instead of reaching Steam.

## Source Reconstruction

Implemented source changes:

- Added `SV_SteamServerEndOrphanedAuthSessions()` to the server-client owner.
- Added `SV_SteamServerClientOwnsAuthSteamId()` to mirror the retail
  server-client table scan using the source `client_t` layout.
- Called `SV_SteamServerEndOrphanedAuthSessions()` from `SV_SpawnServer()`
  immediately after the `Server: %s` startup log and before `CL_MapLoading()`.
- Added a build-disabled no-op stub and exported the declaration through
  `server.h`, so non-Steam builds keep the same spawn sequence safely.
- Expanded platform-service and netcode parity tests to pin the HLIL helper,
  the spawn callsite order, the cleanup body, and the server header surface.

## Confidence

High confidence:

- Retail callsite placement in `SV_SpawnServer`.
- Retail helper ownership and SteamGameServer `EndAuthSession` vtable slot.
- The source cleanup belongs in `sv_client.c` because it needs the server
  client table, SteamID parsing, stats-session cleanup, and auth-session state.

Medium confidence:

- Retail stores auth sessions in a separate SteamID tree, while the source
  tracks retained auth-session ownership per client slot. The reconstruction
  preserves observable behavior for source-owned sessions but does not invent a
  second global tree solely to mirror the retail container shape.

## Validation

- `python -m pytest tests/test_platform_services.py::test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle tests/test_platform_services.py::test_server_spawn_and_shutdown_reconstruct_retail_steam_identity_and_heartbeat_control tests/test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
  - 3 passed.
- `python -m pytest tests/test_platform_services.py tests/test_netcode_parity_manifest.py tests/test_steamworks_harness.py -q --tb=short`
  - 289 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.
- `dumpbin /dependents build\win32\Debug\bin\quakelive_steam.exe`
  - No dynamic `steam_api`, `libpng`, `vorbis`, or `ogg` dependency was present.
- `git diff --check -- src/code/server/sv_client.c src/code/server/sv_init.c src/code/server/server.h tests/test_platform_services.py tests/test_netcode_parity_manifest.py IMPLEMENTATION_PLAN.md docs/reverse-engineering/quakelive_steam_mapping_round_473.md`
  - Passed with repository LF-to-CRLF working-copy warnings only.

## Parity Estimate

- Focused orphaned Steam auth-session cleanup parity: 48% -> 91%.
- Steam launch/runtime integration parity: 80% -> 81%.
