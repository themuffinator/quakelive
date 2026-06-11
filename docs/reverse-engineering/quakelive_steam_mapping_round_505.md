# Quake Live Steam Mapping Round 505: PLAYER_STATS Win/Loss/Played Updates

## Scope

This round reconstructs the first concrete branch inside the
`SteamStats_ProcessEvent` owner restored in Round 504.

The focused retail path is the `PLAYER_STATS` branch in `sub_468030`. This is a
small but important Steam launch/runtime integration island because match-end
qagame report events update the retained per-player Steam GameServer stats
session before the same event is published over ZMQ.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/quakelive_steam_mapping_round_03.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_504.md`
- `src/code/game/g_main.c`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- Retail `sub_468030` recognizes the event name `PLAYER_STATS`.
- The branch materializes the incoming payload into a JSON-like object and
  appends it into the retained player-summary array.
- When a retained SteamID session exists, the branch calls:
  - `sub_467d40(..., 0x51, payload["WIN"])`
  - `sub_467d40(..., 0x52, payload["LOSE"])`
  - `sub_467d40(..., 0x53, 1)`
- The branch then calls `sub_4670c0` to store the pending stats for that
  retained session.
- The writable qagame proxy emits flat integer `WIN` and `LOSE` fields in its
  `PLAYER_STATS` JSON string payload.

## Reconstruction

Implemented changes:

- Added named source constants for the recovered Steam stat IDs:
  `SV_STEAM_STAT_WINS = 0x51`, `SV_STEAM_STAT_LOSSES = 0x52`, and
  `SV_STEAM_STAT_PLAYED = 0x53`.
- Added `SV_SteamStats_ParseEventPayloadInt()` for the source-side flat JSON
  string proxy used by qagame ranking events.
- Added `SV_SteamStats_AddSessionFieldValue()` as the session-keyed
  counterpart to the retail `sub_467d40` helper.
- Added `SV_SteamStats_ProcessPlayerStatsEvent()` to parse `WIN` and `LOSE`,
  update `wins`, `losses`, and `played`, then force a store pass through
  `SV_SteamStats_FlushPendingValues( session, qtrue )`.
- Updated `SV_SteamStats_ProcessEvent()` so `PLAYER_STATS` enters the new
  branch while the remaining retail event families stay mapped but bounded.

## Bounded Behavior

This round intentionally reconstructs only the high-confidence stat island:

- It consumes the source-side JSON string proxy, not the unrecovered retail
  `Json::Value` ABI.
- It maps only the top-level `WIN` and `LOSE` fields plus the constant played
  update.
- It does not yet reconstruct the full `PLAYER_STATS` payload copy into the
  retail summary array or the kill/death/medal branch stat tables.

## Validation

Validation passed:

- `python -m pytest tests/test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - 128 passed.
- `python -m pytest tests/test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_platform_services.py::test_zmq_idzmq_host_round_420_aliases_are_pinned tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - 4 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. The retail HLIL branch, source reconstruction,
static parity coverage, Steamworks harness, and x86 build were sufficient for
this non-visual mapping pass.

## Confidence

High confidence for the focused stat updates:

- The exact retail stat IDs, source payload fields, and flush call are visible
  in Binary Ninja HLIL and now pinned by static tests.

Medium confidence for the broader event processor:

- `PLAYER_STATS` now has real source behavior for the win/loss/played island,
  but the full event processor remains branch-by-branch reconstruction work.

## Parity Estimate

Focused `PLAYER_STATS` win/loss/played branch:

- Before: 35%
- After: 82%

Bounded `SteamStats_ProcessEvent` source coverage:

- Before: 62%
- After: 68%

Overall Steam launch/runtime integration:

- Before: 90.6%
- After: 90.7%
