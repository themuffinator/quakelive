# Quake Live Steam Mapping Round 501: Server Achievement Set Ready Guard

## Scope

This round maps and reconstructs the server-side Steam achievement setter used
by retail Quake Live after `GSStatsReceived_t` has made current stats and
achievements available.

The focused retail path is `sub_4672d0`, reached from the high-level
achievement unlock wrapper `sub_467e00`. This is part of Steam launch/runtime
integration because per-player achievement unlocks must not mutate the local
achievement cache before the GameServer stats backend has reported that the
session is ready.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- `sub_4670c0` is gated by the same ready flag at `arg1 + 0x20` and calls
  `SteamGameServerStats()->StoreUserStats` at vtable slot `0x24`.
- `sub_4672d0` returns false immediately when `arg1 + 0x20` is zero.
- When ready, `sub_4672d0` calls `SteamGameServerStats()->SetUserAchievement`
  at slot `0x1c`, passing the two SteamID halves and an achievement name from
  `data_561c00`.
- `sub_4672d0` then calls `sub_4670c0(arg1)` and returns the result of the
  achievement setter, not the store result.
- The high-level unlock wrapper only writes the local achievement-owned bit
  after `sub_4672d0` returns true.

## Reconstruction

Implemented changes:

- Added a `forceStore` path to `SV_SteamStats_FlushPendingValues()` so the
  server achievement-set helper can mirror retail's store-after-set behavior
  even when no queued stat deltas are pending.
- Added `SV_SteamStats_SetAchievement()` as the source-level counterpart to
  retail `sub_4672d0`: it checks the ready flag, calls
  `QL_Steamworks_ServerSetUserAchievement()`, forces a store pass, and returns
  the setter result.
- Changed `SV_SteamStats_UnlockAchievement()` so it no longer marks the local
  achievement bit or reports success until the baseline query succeeds and the
  server achievement setter returns true.
- Strengthened static parity coverage for the `sub_4670c0`, `sub_4672d0`, and
  `sub_467e00` address sequence, plus the source helper, forced-store, and
  local-cache ordering.

## Validation

Validation passed:

- `python -m pytest tests/test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - 128 passed.
- `python -m pytest tests/test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - 2 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. The retail HLIL branch, source reconstruction,
static parity coverage, Steamworks harness, and x86 build were sufficient for
this non-visual mapping pass.

## Confidence

High confidence for the server achievement set ready guard:

- The ready flag, `SetUserAchievement` slot `0x1c`, forced store helper, and
  caller-side local-cache write are all present in the Binary Ninja HLIL and are
  now pinned by static tests.

Medium confidence for the broader achievement lifecycle:

- The direct server-set path now follows retail, but the legacy dirty
  achievement loop remains available as compatibility scaffolding until the
  remaining event/report paths around `sub_468030` are walked in the same
  detail.

## Parity Estimate

Focused server achievement-set path:

- Before: 82%
- After: 97%

Overall Steam launch/runtime integration:

- Before: 90.2%
- After: 90.3%
