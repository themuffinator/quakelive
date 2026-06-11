# Quake Live Steam Mapping Round 503: Direct Achievement Unlock Dispatch

## Scope

This round maps and reconstructs the high-level server achievement unlock
wrapper used by retail Quake Live after the retained Steam stats session has
been created and made ready.

The focused retail path is `sub_467e00`, which reaches the server achievement
setter recovered in Round 501 as `sub_4672d0`. This round refines the earlier
source interpretation by removing a reconstructed server-side achievement
baseline query from the unlock dispatch path; that live read belongs to other
mapping support and not to retail `sub_467e00`.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_03.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_04.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_501.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_502.md`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- `sub_467e00` starts from the caller-provided SteamID low/high pair and looks
  up the retained stats session through the `data_e30390` owner tree.
- The helper keeps the recovered gameplay gates: `g_gameState` equal to
  `IN_PROGRESS`, `g_training` enabled, or `practiceflags` non-zero.
- In the server-owned branch, `sub_467e00` calls
  `sub_4672d0(*sub_467c50(&data_e30390, &arg1), arg3)`.
- The local achievement-owned bit is written only after the setter result is
  true.
- `sub_467e00` does not call `SteamGameServerStats()` directly, does not call
  `GetUserAchievement`, and does not invoke the passive cached query helper
  `sub_467f70`.
- The passive duplicate/read behavior is represented by `sub_467f70`, mapped in
  Round 502, rather than by the high-level unlock dispatch itself.

## Reconstruction

Implemented changes:

- Changed `SV_SteamStats_UnlockAchievement()` so the active-session path
  directly calls `SV_SteamStats_SetAchievement( session, achievementId )`.
- Removed the non-retail `SV_SteamStats_LoadAchievement()` preflight from the
  unlock helper.
- Removed the unlock helper's internal `already unlocked` early return, keeping
  duplicate suppression with the qagame/query-side ownership checks rather than
  the retail dispatch helper.
- Preserved the local cache write ordering: the reconstructed path marks
  `achievementUnlocked` and `achievementLoaded` only after the setter succeeds.
- Strengthened static parity coverage so the retail `sub_467e00` slice and
  source unlock block both reject `GetUserAchievement`/load-query behavior.

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

High confidence for direct server achievement unlock dispatch:

- The HLIL, source helper boundaries, and static tests now agree that
  `sub_467e00` dispatches through the ready-guarded setter and performs no
  server-side achievement baseline read before setting.

Medium confidence for the broader achievement lifecycle:

- The direct set/query division is now clearer, but later event/report paths
  around the remaining Steam stats callbacks still deserve dedicated mapping
  before the full achievement lifecycle is considered closed.

## Parity Estimate

Focused direct achievement-unlock dispatch:

- Before: 86%
- After: 98%

Overall Steam launch/runtime integration:

- Before: 90.4%
- After: 90.5%
