# Quake Live Steam Mapping Round 540: SteamStats Owner Alias Bridge

## Scope

This pass tightens the Steam GameServerStats owner band in retail
`quakelive_steam.exe`. The focus is the `idSteamStats` session lifecycle,
server-side stats callbacks, per-player stat/achievement mutation helpers, and
the match-summary broadcast path already reconstructed in `sv_client.c` and
`platform_steamworks.c`.

| Retail address | Ghidra name | Binary Ninja name | Promoted name | Confidence |
| --- | --- | --- | --- | --- |
| `0x004670c0` | `FUN_004670c0` | `sub_4670c0` | `SteamStats_FlushPendingValues` | High |
| `0x00467190` | not emitted as `FUN_*` row | `sub_467190` | `SteamStats_OnServersConnected` | Medium-High |
| `0x004671d0` | `FUN_004671d0` | `sub_4671d0` | `SteamStats_OnStatsReceived` | High |
| `0x004672d0` | `FUN_004672d0` | `sub_4672d0` | `SteamStats_SetAchievement` | High |
| `0x00467360` | `FUN_00467360` | `sub_467360` | `SteamStats_OnStatsStored` | High |
| `0x00467560` | `FUN_00467560` | `sub_467560` | `SteamStats_Shutdown` | High |
| `0x00467850` | `FUN_00467850` | `sub_467850` | `SteamStats_Init` | High |
| `0x00467b10` | `FUN_00467b10` | `sub_467b10` | `SteamStats_RemovePlayerSession` | High |
| `0x00467bb0` | `FUN_00467bb0` | `sub_467bb0` | `SteamStats_ClearPendingSummaryState` | High |
| `0x00467cd0` | `FUN_00467cd0` | `sub_467cd0` | `SteamStats_CreatePlayerSession` | High |
| `0x00467d40` | `FUN_00467d40` | `sub_467d40` | `SteamStats_AddFieldValue` | High |
| `0x00467e00` | `FUN_00467e00` | `sub_467e00` | `SteamStats_UnlockAchievement` | High |
| `0x00467f70` | `FUN_00467f70` | `sub_467f70` | `SteamStats_HasAchievement` | High |
| `0x00468030` | `FUN_00468030` | `sub_468030` | `SteamStats_ProcessEvent` | High |
| `0x00468ee0` | `FUN_00468ee0` | `sub_468ee0` | `SteamStats_BroadcastSummary` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records concrete rows for every promoted `FUN_*` entry in this pass, from
  the 30-byte summary clear helper at `0x00467bb0` through the 3753-byte
  `SteamStats_ProcessEvent` body at `0x00468030`.
- Binary Ninja HLIL names the same retail bodies as `sub_*` functions and
  shows the owner relationships:
  - `sub_4670c0` gates on the stats-ready flag and stores pending user stats
    through the GameServerStats store slot.
  - `sub_4671d0` processes `GSStatsReceived_t`, loads stat/achievement values,
    and marks the session ready.
  - `sub_4672d0` sets one achievement and immediately flushes pending values.
  - `sub_467360` handles `GSStatsStored_t`, including the partial-failure
    path that re-enters stats-received handling.
  - `sub_468030` consumes `PLAYER_STATS`, `PLAYER_DEATH`, `PLAYER_KILL`, and
    `PLAYER_MEDAL` events.
  - `sub_468ee0` attaches pending player events to match summaries and sends
    them through the GameServer networking send path.
- `imports.txt` confirms the owning Steam import surface through
  `SteamGameServerStats` and `SteamGameServerNetworking`.

Inferred meaning:

- The reconstructed source keeps the retail owner split: the platform layer
  owns direct GameServerStats vtable calls, while server code owns player
  sessions, stat deltas, achievements, event parsing, and summary broadcast.
- `sub_467190` is retained as a Binary Ninja-only alias because the committed
  Ghidra `functions.csv` does not emit a matching `FUN_00467190` row.
- The small raw CCallback destructor thunks at `0x00467430`, `0x00467460`, and
  `0x00467490` remain deliberately unpromoted until a stable source-owner name
  is needed; their callback object behavior remains covered by HLIL assertions.

## Reconstruction

- Promoted Ghidra-style aliases for the SteamStats owner rows emitted by
  `functions.csv`, including `FUN_004670c0`, `FUN_004671d0`,
  `FUN_004672d0`, `FUN_00467360`, `FUN_00467560`, `FUN_00467850`,
  `FUN_00467b10`, `FUN_00467bb0`, `FUN_00467cd0`, `FUN_00467d40`,
  `FUN_00467e00`, `FUN_00467f70`, `FUN_00468030`, and `FUN_00468ee0`.
- Added lower-case Binary Ninja spellings for the same stable `SteamStats_*`
  source-owner names where the existing alias corpus only had upper-case
  hex-letter variants.
- Strengthened
  `test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge`
  so it now cross-checks:
  - aliases from `references/analysis/quakelive_symbol_aliases.json`;
  - Ghidra `functions.csv` rows and byte-size anchors;
  - existing retail HLIL anchors for callbacks, event processing, summary
    broadcast, and GameServerStats vtable ownership;
  - the reconstructed platform/server source contract.

## Remaining Boundary

This pass is evidence and naming reconstruction only. It does not enable live
Steam stats submission by default; all Steam online-service behavior remains
behind the existing policy and build gates.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json`
- `python -m pytest tests\test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge -q --tb=short`
- `python -m pytest tests\test_platform_services.py -q --tb=short`
- `python -m pytest tests\test_steamworks_harness.py -q --tb=short`

No runtime launch was performed; committed retail HLIL, Ghidra metadata, and
source parity tests were sufficient.

## Parity Estimate

- Focused SteamStats owner alias bridge:
  **before 74% -> after 99%**
- Focused GameServerStats Ghidra/Binary Ninja evidence coverage:
  **before 91% -> after 98%**
- Overall Steam launch/runtime reconstruction parity:
  **before 92.0% -> after 92.05%**
