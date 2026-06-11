# Quake Live Steam Mapping Round 525: GameServer Frame Published-State Pump

## Scope

This pass tightens the Steam GameServer runtime frame owner around
`SteamServer_Frame` (`sub_466850`) and its immediate published-state refresh
call into `SteamServer_UpdatePublishedState` (`sub_466260`). The goal is to
make the source frame pump match the retail owner ordering without enabling
live Steam services by default.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x00466260` | `FUN_00466260` / `sub_466260` | `SteamServer_UpdatePublishedState` | High |
| `0x00466850` | `FUN_00466850` / `sub_466850` | `SteamServer_Frame` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00466260` at `0x00466260`, size `1425`, and `FUN_00466850` at
  `0x00466850`, size `827`.
- Binary Ninja HLIL for `sub_466850` gates on the retained GameServer
  initialized flag, calls `SteamGameServer_RunCallbacks()`, then immediately
  calls `sub_466260(0)` before the keepalive, P2P relay, and outgoing packet
  drain work.
- The same HLIL frame owner then checks the ten-second keepalive interval,
  sends `"that's a good-ass dog"` through `SteamGameServerNetworking` on
  reliable channel `16`, relays channel `1` P2P packets, and drains outgoing
  GameServer UDP packets through vtable slot `0x98`.
- `sub_466260` owns the runtime published-state sweep: max players, password
  state, server/map names, game description, game tags, score key-values,
  player user-data, and bot count.

Inferred meaning:

- The reconstructed `SV_SteamServerNetworkingFrame()` is the source-level
  counterpart to retail `SteamServer_Frame`, so the published-state refresh
  belongs in that helper directly after `QL_Steamworks_RunServerCallbacks()`.
- Keeping the refresh inside the Steam server frame owner avoids a source-only
  split where callbacks were pumped in one helper while the retail
  `sub_466260(0)` side effect happened later in `SV_Frame`.

## Reconstruction

- Promoted paired Ghidra aliases for the two already-named Steam server frame
  owners:
  - `FUN_00466260 -> SteamServer_UpdatePublishedState`
  - `FUN_00466850 -> SteamServer_Frame`
- Moved the source `SV_SteamServerUpdatePublishedState( qfalse )` call into
  `SV_SteamServerNetworkingFrame()` immediately after
  `QL_Steamworks_RunServerCallbacks()`.
- Removed the later `SV_Frame()` duplicate call so the retained source has one
  runtime published-state sweep in the retail frame owner.
- Strengthened `tests/test_platform_services.py` to pin alias coverage,
  Ghidra function-size rows, and the source ordering:
  `RunServerCallbacks -> UpdatePublishedState(false) -> keepalive/P2P/drain`.

## Remaining Boundary

Retail calls `sub_466850` from the common frame loop before the broader server
frame work. This source tree still invokes `SV_SteamServerNetworkingFrame()`
from `SV_Frame()` after the normal `com_sv_running` guard. This pass preserves
that existing architecture and only closes the retail-local side-effect order
inside the Steam server frame helper.

Follow-up: round 527 closes this caller-placement boundary by moving the
source call into `Com_Frame()`.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json`
- `python -m pytest tests\test_platform_services.py::test_server_frame_reconstructs_retail_steam_server_owner tests\test_platform_services.py::test_server_published_state_reconstructs_retail_steam_server_owner -q --tb=short`

## Parity Estimate

- Focused Steam GameServer frame published-state ordering confidence:
  **before 82% -> after 98%**.
- Focused Steam server frame Ghidra/Binary Ninja alias bridge confidence:
  **before 50% -> after 98%**.
- Overall Steam launch/runtime integration confidence:
  **before 91.5% -> after 91.6%**.
