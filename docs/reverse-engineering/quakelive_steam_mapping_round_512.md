# Quake Live Steam Mapping Round 512: PLAYER_DEATH Event Cache

## Scope

This round reconstructs the next Steam stats runtime branch around retail
`SteamStats_ProcessEvent` (`sub_468030`): the `PLAYER_DEATH` path that builds a
bounded pending event array later attached to match reports as `PLYR_EVENTS`.

The source work stays behind the existing retained server Steam stats owner and
does not enable live Quake Live service behavior.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`

Observed facts:

- Retail `sub_468030` recognizes `PLAYER_DEATH` at `0x0046826b`.
- The branch appends only while `sub_429c90(&data_e30380) < 0x3e8`, so the
  pending death-event cache is bounded at 1000 entries.
- The death object copies root `TIME` and `MOD`.
- It copies nested `KILLER` and `VICTIM` identity/team fields, renaming nested
  `STEAM_ID` to the report-side `ID` field in the native Json object.
- It copies nested `POWERUPS` arrays when present.
- Retail `sub_468ee0` later attaches `data_e30380` as `PLYR_EVENTS` and clears
  it with `sub_429d90`.
- Retail qagame death publishing uses root `MOD`, nested per-player `WEAPON`,
  and emits nested `POWERUPS` arrays by walking powerup ids from the observed
  retail loop range beginning at id `4`.

## Reconstruction

Implemented changes:

- Added `G_RankBuildPlayerPowerupsArray()` in `src/code/game/g_main.c` and
  wired `POWERUPS` into the shared `PLAYER_KILL` / `PLAYER_DEATH` per-player
  summary object.
- Corrected the root death payload key from source-only `WEAPON` to retail
  `MOD`; nested per-player weapon fields remain a separate retail gap.
- Added a bounded source-side `sv_steam_player_death_event_t` cache in
  `src/code/server/sv_client.c`, mirroring retail `data_e30380` capacity.
- Added nested payload readers for integer, string, and array fields used by
  the cache.
- Wired `PLAYER_DEATH` recording before SteamID/session gating in
  `SV_SteamStats_ProcessEvent()`, matching the retail branch position before
  retained-session lookup.
- Added `SV_SteamStats_ProcessMatchReport()` and called it from
  `SV_SubmitMatchReport()` before ZMQ publication so cached death events are
  cleared at the match-report boundary.
- Strengthened static coverage for Binary Ninja/Ghidra evidence, qagame payload
  shape, cache bounds, pre-session dispatch order, match-report ordering, and
  build-disabled stubs.

## Remaining Gaps

- Source does not yet inject cached events into the serialized qagame
  `MATCH_REPORT` payload as `PLYR_EVENTS`. Retail mutates a native
  `Json::Value`; the writable source currently forwards serialized JSON text.
- The retail state guard at `*(data_13e1804 + 0x30) != 2` is still mapped but
  not assigned to a stable source owner.
- The qagame per-player death object remains reduced compared with retail:
  nested `WEAPON`, `AIRBORNE`, `AMMO`, `VIEW`, `HOLDABLE`, bot skill, and
  several achievement side effects are still later reconstruction work.

## Validation

Validation passed:

- `python -m pytest tests\test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_platform_services.py -q --tb=short`
  - 134 passed.
- `python -m pytest tests\test_steamworks_harness.py -q --tb=short`
  - 128 passed.
- `python -m pytest tests\test_game_exit_rules_parity.py -q --tb=short`
  - 10 passed.
- `MSBuild.exe src\code\quakelive_steam.vcxproj /m /p:Configuration=Debug /p:Platform=x86`
  - Build succeeded, 0 warnings, 0 errors.
- `MSBuild.exe src\code\game\qagamex86.vcxproj /m /p:Configuration=Debug /p:Platform=x86`
  - Build succeeded, 0 warnings, 0 errors.

## Confidence

Focused `PLAYER_DEATH` pending-event cache reconstruction:

- Before: 8%
- After: 68%

Bounded `SteamStats_ProcessEvent` source coverage:

- Before: 82%
- After: 85%

Overall Steam launch/runtime integration confidence:

- Before: 91.1%
- After: 91.2%
