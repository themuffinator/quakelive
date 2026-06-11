# Quake Live Steam Mapping Round 502: Passive Achievement Query Cache Read

## Scope

This round maps and reconstructs the server-side Steam achievement query helper
used by retail Quake Live when qagame asks whether a player already owns an
achievement.

The focused retail path is `sub_467f70`, reached by the server-facing
`SV_ClientHasSteamAchievement` wrapper. This is part of Steam launch/runtime
integration because qagame achievement gates must observe the retained
per-player Steam stats session without creating a new session or issuing a live
backend query from the read path.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_03.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_04.md`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- `sub_467f70` returns `0` immediately when both SteamID words are zero.
- It searches the retained `data_e30390` stats-session tree using the SteamID
  low/high pair.
- It only reads the local achievement bit when a session exists and the ready
  flag at `session + 0x20` is set.
- It returns the cached achievement bit at `session + 0x1c + index * 8 + 4`.
- No `RequestUserStats`, `GetUserAchievement`, or session-creation path is
  visible in the helper.

## Reconstruction

Implemented changes:

- Changed `SV_SteamStats_HasAchievement()` into a passive cache read.
- The function now validates the live client, parses its SteamID, finds the
  existing retained stats session by SteamID, requires `backendAvailable`, and
  returns the cached achievement bit.
- Removed the query path's session creation and `SV_SteamStats_LoadAchievement`
  side effect, keeping live backend loads limited to the explicit unlock/source
  helper paths.
- Strengthened static coverage for the `sub_467f70` zero-ID, session lookup,
  ready-flag, cached-bit, and false-return branches.

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

High confidence for the query helper:

- The source path now matches the retail helper's read-only shape: existing
  session, ready flag, cached bit, otherwise false.

Medium confidence for full achievement ownership warmup:

- The query helper no longer overreaches, but the broader achievement table
  initialization around `GSStatsReceived_t` and event/report processing still
  deserves a later dedicated walk before the whole achievement lifecycle can be
  called closed.

## Parity Estimate

Focused passive achievement-query path:

- Before: 74%
- After: 96%

Overall Steam launch/runtime integration:

- Before: 90.3%
- After: 90.4%
