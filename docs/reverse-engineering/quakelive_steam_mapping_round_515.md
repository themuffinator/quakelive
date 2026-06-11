# Quake Live Steam Mapping Round 515: PLYR_EVENTS Match-Report Merge

## Scope

This round closes the next Steam stats runtime gap left by Round 512: retail
`SteamStats_BroadcastSummary` (`sub_468ee0`) attaches cached `PLAYER_DEATH`
events to the outgoing match report under `PLYR_EVENTS` before clearing the
pending event array.

The source reconstruction remains a bounded compatibility path. It does not
enable live Quake Live services and keeps Steam/online behavior behind the
existing `QL_BUILD_ONLINE_SERVICES` policy.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `docs/reverse-engineering/quakelive_steam_mapping_round_512.md`

Observed facts:

- Retail `sub_468030` appends normalized `PLAYER_DEATH` event objects into
  `data_e30380` through `sub_42a410(&data_e30380, &var_cc)`.
- The cached event branch is bounded by `sub_429c90(&data_e30380) < 0x3e8`.
- The event object carries root `TIME` and `MOD`.
- Nested `KILLER` and `VICTIM` objects copy `NAME`, `TEAM`, and `POWERUPS`;
  nested `STEAM_ID` is renamed to `ID` in the cached native Json object.
- Retail `sub_468ee0` attaches `data_e30380` with
  `sub_4296c0(sub_42a110(&var_50, "PLYR_EVENTS"), &data_e30380)`.
- The same match-report path clears both pending arrays afterward through
  `sub_429d90(&data_e303a0)` and `sub_429d90(&data_e30380)`.

## Reconstruction

Implemented changes:

- Changed `SV_SteamStats_ProcessMatchReport()` from a notify-only hook into a
  prepare-and-return hook. It now returns the payload pointer that the shared
  stats publication path should forward.
- Added bounded server-side JSON append and escape helpers for the serialized
  qagame report proxy.
- Added a root-object close finder so the Steam stats owner can splice
  `PLYR_EVENTS` into an existing match-report object without mutating the
  qagame-owned stack buffer.
- Serialized cached death events into the retail report-side shape:
  `TIME`, `MOD`, nested `KILLER` / `VICTIM`, nested `ID`, `TEAM`, and
  `POWERUPS`.
- Updated `SV_SubmitMatchReport()` to use a local `MAX_MSGLEN` staging buffer
  and forward the prepared report pointer to `Zmq_SubmitMatchReport()`.
- Preserved fallback behavior: if the report is malformed, already has
  `PLYR_EVENTS`, or the staging buffer is too small, the original report is
  forwarded and the pending death-event cache is still cleared at the retail
  boundary.
- Updated the build-disabled stub to return the original report unchanged.

## Remaining Gaps

- Retail transmits the serialized report through Steam GameServerNetworking
  peers. The source still publishes through the retained ZMQ stats lane unless
  a future pass reconstructs the Steam P2P summary fanout.
- The retail state guard at `*(data_13e1804 + 0x30) != 2` remains mapped but
  not assigned to a stable source owner.
- The qagame per-player death object is still reduced compared with retail for
  nested `WEAPON`, `AIRBORNE`, `AMMO`, `VIEW`, `HOLDABLE`, bot skill, and some
  achievement-adjacent details.

## Validation

Validation completed:

- `python -m pytest tests\test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge tests\test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests\test_platform_services.py::test_zmq_idzmq_host_round_420_aliases_are_pinned -q --tb=short`
  - 3 passed.
- `python -m pytest tests\test_game_exit_rules_parity.py::test_log_exit_runs_rank_match_report_once_after_player_stats -q --tb=short`
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

Focused `PLYR_EVENTS` match-report merge reconstruction:

- Before: 0%
- After: 76%

Focused Steam stats match-report owner coverage:

- Before: 35%
- After: 78%

Overall Steam launch/runtime integration confidence:

- Before: 91.2%
- After: 91.3%
