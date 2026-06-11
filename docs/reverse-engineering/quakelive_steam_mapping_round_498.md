# Quake Live Steam Mapping Round 498: GameServer Stats Logged-On Gate

## Scope

This round maps and reconstructs the retail `SteamGameServerStats`
`RequestUserStats` gate used by the server stats runtime. The retail path first
checks the GameServerStats owner, then asks `SteamGameServer()->BLoggedOn`, then
reacquires GameServerStats before dispatching the request through vtable slot
`0x00`.

This sits on the Steam launch/runtime boundary because dedicated-server stats
requests must stay cold until the Steam GameServer runtime and stats interface
are both available.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/common/platform/platform_steamworks.c`
- `tests/steamworks_harness.c`
- `tests/test_platform_services.py`
- `tests/test_steamworks_harness.py`

Observed facts:

- Ghidra imports include `STEAM_API.DLL!SteamGameServerStats @ 0015932c`.
- Retail HLIL function `sub_467190` calls `SteamGameServerStats()` at
  `0046719a`.
- Only after that non-null check does retail call
  `(*(*SteamGameServer() + 0x20))()` at `004671ad`.
- Retail checks the byte result, calls `SteamGameServerStats()` again at
  `004671b3`, then dispatches `RequestUserStats` via the first vtable slot at
  `004671c3`.
- SRP already used the correct GameServerStats request vtable slot, but the
  wrapper checked the logged-on state before probing the stats owner.

## Reconstruction

Implemented changes:

- Reordered `QL_Steamworks_ServerRequestUserStats()` so the first
  `QL_Steamworks_GetGameServerStatsInterface()` probe happens before
  `QL_Steamworks_ServerIsLoggedOn()`.
- Kept the second GameServerStats acquisition after the logged-on check to
  mirror retail's repeated `SteamGameServerStats()` call before vtable slot
  `0x00` dispatch.
- Extended the Steamworks harness with:
  - a toggle for GameServerStats interface availability,
  - an interface acquisition counter,
  - exported accessors for the new probe state.
- Added an executable regression proving:
  - pre-init stats requests do not call either GameServerStats or BLoggedOn,
  - missing GameServerStats prevents the BLoggedOn call,
  - a false BLoggedOn result prevents `RequestUserStats`,
  - a successful request touches GameServerStats twice and calls the request
    slot once.
- Strengthened static parity checks with the Ghidra import and Binary Ninja
  HLIL address sequence.

## Validation

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_game_server_stats_request_matches_retail_logged_on_gate_order tests/test_steamworks_harness.py::test_game_server_stats_wrappers_use_retail_gameserverstats_slots -q --tb=short`
  - 4 passed across disabled and enabled Steamworks harness builds.
- `python -m pytest tests/test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - 128 passed.
- `python -m pytest tests/test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - 2 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.
- `git diff --check -- src/common/platform/platform_steamworks.c tests/steamworks_harness.c tests/test_steamworks_harness.py tests/test_platform_services.py IMPLEMENTATION_PLAN.md docs/reverse-engineering/quakelive_steam_mapping_round_498.md`
  - No whitespace errors; Git reported CRLF normalization warnings for tracked
    text files.

No game launch was performed. Static retail evidence plus harness-level runtime
coverage are sufficient for this source reconstruction pass.

## Confidence

High confidence for the focused request gate:

- Import evidence, HLIL address order, source ordering, and executable harness
  counters now agree.

Medium confidence for the wider dedicated stats lifecycle:

- This pass pins the request gate. It does not remap every server stats
  callback, session cache, or achievement flush edge.

## Parity Estimate

Focused Steam GameServer stats logged-on request gate:

- Before: 87%
- After: 98%

Overall Steam launch/runtime integration:

- Before: 89.9%
- After: 90.0%
