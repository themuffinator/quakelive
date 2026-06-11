# Quake Live Steam Mapping Round 508: PLAYER_KILL Speed Achievement Gate

## Scope

This round extends the bounded `SteamStats_ProcessEvent` reconstruction with
the first high-confidence `PLAYER_KILL` achievement side effect.

The focused retail path unlocks `AW_SPEED_KILLS` when the event is a normal
kill rather than a suicide or teamkill, the retained Steam stats session does
not already own achievement id `1`, and nested payload field `KILLER.SPEED` is
greater than `500`.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `src/code/game/g_main.c`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- Retail `sub_468030` recognizes event name `PLAYER_KILL` at `0x00468872`.
- The branch is skipped when the server state field at `data_13e1804[0xc]`
  equals `2`; the source reconstruction remains bounded to events already
  delivered through qagame's normal ranking publisher.
- The branch reads `SUICIDE` and `TEAMKILL` through boolean helpers with
  default-false values.
- The achievement side effect is inside the non-suicide/non-teamkill branch.
- Retail checks `sub_467f70(..., 1) == 0`, then reads
  `payload["KILLER"]["SPEED"]`.
- The speed comparison is signed integer/number conversion greater than
  `0x1f4`, and success calls `sub_467e00(..., 1)`.
- Source qagame publishes `TEAMKILL`, `SUICIDE`, and a nested `KILLER` object;
  `G_RankBuildPlayerSummaryObject()` emits `SPEED` as a float field.
- Source achievement index `1` maps to `AW_SPEED_KILLS` in the recovered
  achievement descriptor table.

## Reconstruction

Implemented changes:

- Added named source constants for `SV_STEAM_ACHIEVEMENT_SPEED_KILLS` and
  `SV_STEAM_PLAYER_KILL_SPEED_THRESHOLD`.
- Added bounded payload helpers for source-side qagame JSON proxies:
  flat field lookup, boolean parsing, nested object field lookup, and nested
  float parsing.
- Added `SV_SteamStats_ProcessPlayerKillEvent()` to mirror the recovered
  `PLAYER_KILL` speed achievement gate:
  parse `TEAMKILL` and `SUICIDE`, skip either case, check retained achievement
  cache for id `1`, parse `KILLER.SPEED`, and unlock when the value is greater
  than `500`.
- Wired `SV_SteamStats_ProcessEvent()` so `PLAYER_KILL` now enters the new
  source-backed branch after `PLAYER_STATS`.
- Strengthened static parity coverage for the retail address sequence,
  qagame payload producer, parser helpers, branch predicates, and dispatch
  ordering.

## Bounded Behavior

This remains behind `QL_BUILD_ONLINE_SERVICES`, default disabled.

The adjacent retail weapon stat table updates are still mapped-only. They
depend on recovered string-to-stat lookup tables around `data_561a04`,
`data_561a08`, and `data_561a0c`, so this pass intentionally reconstructs only
the achievement side effect with direct HLIL and source-payload support.

The source reconstruction consumes the qagame-side JSON string proxy instead of
recreating the retail `Json::Value` ABI.

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

No game launch was performed. The committed retail HLIL/Ghidra evidence, source
static coverage, Steamworks harness, and x86 build were sufficient for this
non-visual mapping pass.

## Confidence

High confidence for the focused speed achievement gate:

- The event name, suicide/teamkill predicates, achievement id, nested field
  path, speed constant, comparison, and unlock call are all visible in Binary
  Ninja HLIL and now pinned by static tests.

Medium confidence for the wider `PLAYER_KILL` event processor:

- The speed achievement side effect is source-backed, while the weapon stat
  table increments and broader kill/death/medal tables remain branch-by-branch
  reconstruction work.

## Parity Estimate

Focused `PLAYER_KILL` `AW_SPEED_KILLS` gate:

- Before: 15%
- After: 84%

Bounded `SteamStats_ProcessEvent` source coverage:

- Before: 75%
- After: 78%

Overall Steam launch/runtime integration:

- Before: 90.9%
- After: 91.0%
