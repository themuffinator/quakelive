# Quake Live Steam Mapping Round 507: PLAYER_STATS Training Achievement Gate

## Scope

This round extends the `PLAYER_STATS` branch of retail
`SteamStats_ProcessEvent` with the training-map achievement gate that appears
immediately before the `AW_WICKED` score branch reconstructed in Round 506.

The focused retail path unlocks `AW_TRAINING_3_2` when a retained Steam stats
session does not already own the achievement, the active map is `qztraining`,
training mode is enabled, and the `PLAYER_STATS` payload reports a truthy
`WIN` field.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- Retail `sub_468030` checks `sub_467f70(..., 9) == 0` before evaluating the
  training gate.
- The branch compares the current `mapname` cvar string to `qztraining` using
  a bytewise string comparison.
- The branch requires `sub_4ccd80("g_training") > 0`.
- It reads payload field `WIN` through the same recovered field name used by
  the win/loss/played stat update island.
- It applies a truthiness helper to the `WIN` value, then calls
  `sub_467e00(..., 9)` when the predicate succeeds.
- Source achievement index `9` maps to `AW_TRAINING_3_2` in the recovered
  achievement descriptor table.

## Reconstruction

Implemented changes:

- Added named constants for `SV_STEAM_ACHIEVEMENT_TRAINING_3_2` and
  `SV_STEAM_PLAYER_STATS_TRAINING_MAP`.
- Extended `SV_SteamStats_ProcessPlayerStatsEvent()` so the recovered
  win/loss/played store is followed by the retail-order training gate:
  retained cache absent, `mapname == "qztraining"`, `g_training > 0`,
  `WIN != 0`, then unlock achievement `9`.
- Reused the session-level achievement cache and unlock helpers introduced in
  Round 506, preserving retail's split between `sub_467f70` passive cache read
  and `sub_467e00` gameplay-gated unlock dispatch.
- Strengthened static parity coverage for the retail address sequence, source
  predicates, and branch ordering relative to the `AW_WICKED` gate.

## Bounded Behavior

The branch remains behind `QL_BUILD_ONLINE_SERVICES`, default disabled.

The source reconstruction consumes the qagame-side flat JSON string payload
instead of recreating the retail `Json::Value` ABI. For this branch, the
source-side `WIN != 0` predicate is the bounded equivalent of retail's
truthiness helper on the same logical field.

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

High confidence for the focused training achievement gate:

- The achievement id, map string, training cvar, `WIN` field, truthiness
  predicate, and unlock call are all visible in Binary Ninja HLIL and now
  pinned by static tests.

Medium confidence for the wider `PLAYER_STATS` event processor:

- The win/loss/played island and two achievement side effects are now
  source-backed. The retained summary-array behavior and the remaining
  kill/death/medal event families still need branch-by-branch reconstruction.

## Parity Estimate

Focused `PLAYER_STATS` `AW_TRAINING_3_2` gate:

- Before: 18%
- After: 87%

Bounded `SteamStats_ProcessEvent` source coverage:

- Before: 72%
- After: 75%

Overall Steam launch/runtime integration:

- Before: 90.8%
- After: 90.9%
