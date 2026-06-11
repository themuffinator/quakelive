# Quake Live Steam Mapping Round 504: Report Event Steam Stats Bridge

## Scope

This round maps and reconstructs the engine-side report-event bridge that sits
between qagame's typed rankings events and the server-owned Steam stats and ZMQ
publication owners.

The focused retail wrapper is `sub_4E2640`, promoted as
`SV_ReportPlayerEvent`. The focused Steam stats sink is `sub_468030`, promoted
as `SteamStats_ProcessEvent`. This round restores the missing source call
boundary and keeps the deeper event mutation logic bounded for later
branch-by-branch reconstruction.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/quakelive_steam_mapping_round_03.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_95.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_420.md`
- `src/code/server/sv_game.c`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- Retail `sub_4E2640` first calls `sub_468030(arg1, arg2, arg3)`.
- The same wrapper then immediately forwards to `sub_4F4E10`, the retained
  `Zmq_ReportPlayerEvent` wrapper.
- Alias support already names `sub_4E2640` as `SV_ReportPlayerEvent` and
  `sub_468030` as `SteamStats_ProcessEvent`.
- `sub_468030` recognizes at least `PLAYER_STATS`, `PLAYER_KILL`,
  `PLAYER_DEATH`, and `PLAYER_MEDAL`.
- The `PLAYER_STATS` branch touches the retained SteamID-keyed session map and
  flushes through `sub_4670c0`.
- The kill/medal branches reuse the passive achievement query helper
  `sub_467f70` and the direct unlock helper `sub_467e00`.

## Reconstruction

Implemented changes:

- Added `SV_SteamStats_ProcessEvent()` as the source-level owner boundary for
  retail `SteamStats_ProcessEvent`.
- Exported the function through `server.h` so the qagame report wrapper can
  reach the server-owned Steam stats module.
- Changed `SV_ReportPlayerEvent()` so it calls
  `SV_SteamStats_ProcessEvent()` before `Zmq_ReportPlayerEvent()`, matching
  retail `sub_4E2640`.
- Added a default-disabled stub that logs through the server stats policy
  labels when online services are not compiled in.
- Added static coverage for the retail event names and the source ordering.

## Bounded Behavior

The new source function intentionally stops at the owner boundary:

- It combines the SteamID low/high words into the retained `CSteamID` value.
- It filters to the retail event families that have Steam-side effects in
  `sub_468030`.
- It looks up the existing retained stats session and logs whether the event
  can be owned by that session.
- It does not yet parse the qagame JSON payload string into the full retail
  `Json::Value` object model.
- It does not yet reconstruct the individual `PLAYER_STATS`, kill/death, or
  medal branch stat increments and achievement gates beyond the already
  recovered lower-level stat and achievement helpers.

This keeps the repo honest: the retail call order is restored, but the full
`sub_468030` branch body remains explicit follow-up work instead of hidden
behind broad assumptions.

## Validation

Validation passed:

- `python -m pytest tests/test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_platform_services.py::test_zmq_idzmq_host_round_420_aliases_are_pinned -q --tb=short`
  - 2 passed.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - 128 passed.
- `python -m pytest tests/test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_platform_services.py::test_zmq_idzmq_host_round_420_aliases_are_pinned tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - 4 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. This was a static mapping/source-boundary pass,
and the committed retail HLIL plus focused static tests are enough for the
claim made here.

## Confidence

High confidence for the wrapper order:

- `sub_4E2640` plainly calls `sub_468030` before `sub_4F4E10`, and the source
  now preserves that order.

Medium confidence for the event processor owner boundary:

- The recognized event names, session-map dependency, and lower-level helper
  calls are visible in retail HLIL. The current source intentionally preserves
  the boundary while leaving detailed payload mutation for later passes.

## Parity Estimate

Focused `SV_ReportPlayerEvent` Steam-stats bridge:

- Before: 58%
- After: 90%

Bounded `SteamStats_ProcessEvent` source coverage:

- Before: 35%
- After: 62%

Overall Steam launch/runtime integration:

- Before: 90.5%
- After: 90.6%
