# Quake Live Steam Mapping Round 681: GameServerStats Value Slot Constants

Date: 2026-06-16

## Scope

This pass rechecked the retail dedicated-server `SteamGameServerStats` value
wrappers and named the remaining stats vtable slots used by SRP's production
Steamworks shim. Earlier rounds reconstructed the initialized guards and
server-stat owner wiring. This round closes the source-shape gap where the
stats wrappers still carried raw `0x00` through `0x24` vtable indices.

Focused parity estimate: **before 90% -> after 99%** for GameServerStats value
ABI source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.70% -> 93.72%**.
Repo-wide parity remains **99%** because this pass clarifies the opt-in
Steamworks lane without changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Observed slot evidence |
| --- | --- | --- |
| `FUN_004670c0` / `sub_4670c0` | `SteamStats_FlushPendingValues` | Flushes dirty int, float, average-rate, achievement, and store work through `SteamGameServerStats`. |
| `sub_467190` | `SteamStats_OnServersConnected` | Checks `SteamGameServerStats()`, gates on `SteamGameServer + 0x20`, reacquires stats, then dispatches request through slot `0x00`. |
| `FUN_004671d0` / `sub_4671d0` | `SteamStats_OnStatsReceived` | Reads current float/int values through slots `0x04` and `0x08`. |
| `FUN_004672d0` / `sub_4672d0` | `SteamStats_SetAchievement` | Sets achievement ownership through `SteamGameServerStats + 0x1c`, then flushes pending values. |
| `FUN_00467850` / `sub_467850` | `SteamStats_Init` | Initializes the stats owner and uses the same request gate once `SteamGameServerStats()` and `SteamGameServer + 0x20` are available. |

Observed facts:

- `functions.csv` contains the mapped retail owners at `004670c0`,
  `004671d0`, `004672d0`, and `00467850`.
- `imports.txt` confirms `STEAM_API.DLL!SteamGameServerStats`.
- Binary Ninja HLIL shows request, get-float, get-int, set-float, set-int,
  average-rate update, set-achievement, and store dispatches through
  `SteamGameServerStats + 0x00`, `+0x04`, `+0x08`, `+0x10`, `+0x14`,
  `+0x18`, `+0x1c`, and `SteamGameServerStats + 0x24`.
- The Steamworks harness exposes the same mock GameServerStats vtable layout.
  Round 713 later promoted that mock layout from raw offsets to named
  harness-local `QLR_STEAM_GAMESERVERSTATS_*` constants, so naming these slots
  does not change behavior.

Inference: the public `QL_Steamworks_Server*` stats wrappers should continue
resolving the same vtable entries, but the production shim should name the
stats ABI slots so later descriptor and callback work can reason about the
interface directly.

## Source Reconstruction

SRP now names the GameServerStats value slots:

- `QL_STEAM_GAMESERVERSTATS_REQUEST_USER_STATS_SLOT`
- `QL_STEAM_GAMESERVERSTATS_GET_USER_STAT_FLOAT_SLOT`
- `QL_STEAM_GAMESERVERSTATS_GET_USER_STAT_INT_SLOT`
- `QL_STEAM_GAMESERVERSTATS_GET_USER_ACHIEVEMENT_SLOT`
- `QL_STEAM_GAMESERVERSTATS_SET_USER_STAT_FLOAT_SLOT`
- `QL_STEAM_GAMESERVERSTATS_SET_USER_STAT_INT_SLOT`
- `QL_STEAM_GAMESERVERSTATS_UPDATE_AVG_RATE_STAT_SLOT`
- `QL_STEAM_GAMESERVERSTATS_SET_USER_ACHIEVEMENT_SLOT`
- `QL_STEAM_GAMESERVERSTATS_STORE_USER_STATS_SLOT`

`QL_Steamworks_ServerRequestUserStats` keeps the retail-shaped request gate:
probe `SteamGameServerStats()`, require `SteamGameServer()->BLoggedOn`, reacquire
`SteamGameServerStats()`, then dispatch request through the named slot.

The get/set/achievement/store wrappers now resolve through the named slots while
retaining their existing argument validation, initialized-state guard, ID word
split, and disabled-build fallbacks.

This pass does not enable live Steam behavior by default. It preserves the
existing `QL_BUILD_STEAMWORKS` and default-disabled `QL_BUILD_ONLINE_SERVICES`
policy.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k "steam_gameserverstats_value_slot_constants_round_681 or steam_gameserver_stats_wrapper_guards_track_round_633 or server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge" --tb=short`:
  3 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short`: 226
  passed.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`: 132
  passed.
- `git diff --check`: passed with CRLF conversion warnings only.
