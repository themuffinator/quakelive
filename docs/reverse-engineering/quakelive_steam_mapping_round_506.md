# Quake Live Steam Mapping Round 506: PLAYER_STATS WICKED Score Gate

## Scope

This round extends the `PLAYER_STATS` branch reconstructed in Round 505 with
the next high-confidence Steam achievement side effect visible in retail
`SteamStats_ProcessEvent`.

The focused retail path is the `AW_WICKED` branch inside `sub_468030`: after
the win/loss/played stat flush, retail checks the retained achievement cache,
gates on one gametype, compares the `SCORE` payload field to a fixed value, and
then dispatches the normal server-owned achievement unlock helper.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- Retail `sub_468030` reaches the `PLAYER_STATS` branch before the
  `PLAYER_KILL`, `PLAYER_DEATH`, and `PLAYER_MEDAL` event families.
- After the recovered win/loss/played updates and `sub_4670c0` store call, the
  branch checks `sub_467f70(..., 0x0e) == 0`.
- The same condition also requires `sub_4ccd80("g_gametype") == 5`.
- The branch constructs integer constant `0x29a` and compares it to
  payload field `"SCORE"` through `sub_429860`.
- HLIL for `sub_429860` shows a typed equality comparison, so the observed
  branch is `SCORE == 666`, not a greater-than-or-equal threshold.
- When the comparison succeeds, retail calls `sub_467e00(..., 0x0e)`.
- Source achievement index `0x0e` maps to `AW_WICKED` in the recovered
  achievement descriptor table.

## Reconstruction

Implemented changes:

- Added named constants for `SV_STEAM_ACHIEVEMENT_WICKED`,
  `SV_STEAM_PLAYER_STATS_WICKED_SCORE`, and
  `SV_STEAM_PLAYER_STATS_WICKED_GAMETYPE`.
- Added `SV_SteamStats_HasSessionAchievement()` as the session-keyed
  counterpart to retail `sub_467f70`, using the retained achievement cache and
  deliberately avoiding a fresh `GetUserAchievement` query.
- Added `SV_SteamStats_UnlockSessionAchievement()` as the event-session
  counterpart to retail `sub_467e00`, preserving the recovered gameplay gate
  before direct `SetAchievement` dispatch.
- Extended `SV_SteamStats_ProcessPlayerStatsEvent()` so the recovered stat
  flush is followed by the `AW_WICKED` gate:
  retained cache absent, `g_gametype == 5`, `SCORE == 666`, then unlock
  achievement `0x0e`.
- Strengthened static parity coverage for the retail address sequence, helper
  behavior, and source ordering.

## Bounded Behavior

This remains a source reconstruction of the online-service lane, which is
contained behind `QL_BUILD_ONLINE_SERVICES` and defaults disabled.

The reconstruction intentionally uses the existing source-side flat JSON string
payload reader rather than attempting to recreate the retail `Json::Value` ABI.
It also leaves the adjacent training-map achievement branch for a later pass,
because that branch has additional mapname and `g_training` dependencies that
deserve their own evidence note.

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

High confidence for the focused `AW_WICKED` gate:

- The achievement id, gametype value, score constant, field name, equality
  helper, and unlock call are all visible in Binary Ninja HLIL and now pinned
  by static tests.

Medium confidence for the wider `PLAYER_STATS` event processor:

- The win/loss/played island and one achievement side effect are now
  source-backed, while the remaining training and summary-array behavior still
  need branch-by-branch reconstruction.

## Parity Estimate

Focused `PLAYER_STATS` `AW_WICKED` gate:

- Before: 20%
- After: 86%

Bounded `SteamStats_ProcessEvent` source coverage:

- Before: 68%
- After: 72%

Overall Steam launch/runtime integration:

- Before: 90.7%
- After: 90.8%
