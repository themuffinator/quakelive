# Quake Live Steam Mapping Round 518: Steam Summary P2P Fanout

## Scope

This round closes the next gap in the retained Steam stats match-report owner:
retail `SteamStats_BroadcastSummary` (`sub_468ee0`) serializes the prepared
match summary and sends it through `SteamGameServerNetworking` to the transient
summary peer tree.

The source reconstruction remains a bounded compatibility path. It does not
enable live Quake Live services by default and still relies on the existing
`QL_BUILD_ONLINE_SERVICES` policy and Steamworks wrapper fallbacks.

## Evidence

Primary evidence:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_515.md`

Observed facts:

- The alias map identifies `sub_468EE0` as `SteamStats_BroadcastSummary`.
- The Ghidra import table contains
  `STEAM_API.DLL!SteamGameServerNetworking @ 001592a6`.
- Retail `sub_468ee0` gates on `sub_465a30()` before touching the Steam summary
  path.
- The same function copies the incoming Json object, checks `TRAINING` and
  `ABORTED`, attaches `PLYR_STATS` and `PLYR_EVENTS`, serializes the Json with
  `sub_42a850(&var_50, &var_24)`, and allocates a contiguous send buffer.
- The summary fanout walks `data_e30374`, reads the stored SteamID halves from
  each node, calls `SteamGameServerNetworking()`, and dispatches
  `(**eax_16)(edi_2, ebx_5, edi_1, var_40, 2, 0)`.
- After the send loop, retail frees the serialized buffer, clears
  `data_e303a0` and `data_e30380`, deletes the `data_e30374` tree nodes, resets
  the sentinel links, and writes `data_e30378 = 0`.
- `hlil_part06` shows `data_e30374` initialized as a `0x20` byte sentinel tree
  with the end/color bytes set and an `atexit` destructor.

Inferred meaning:

- `data_e30374` is a transient recipient set for match-summary P2P fanout, not
  the long-lived stats-session map (`data_e30390`).
- The committed HLIL/Ghidra corpus exposes `data_e30374` initialization,
  drain, and destruction, but not a stable population owner. The source mirror
  therefore tracks pending summary peers at the retained stats-session
  bootstrap/reuse boundary, which is the closest stable source owner already
  tied to the retail `"hello"` P2P handshake.

## Reconstruction

Implemented changes:

- Added explicit source constants for the summary recipient mirror:
  `SV_STEAM_STATS_SUMMARY_PEER_LIMIT`, send type `2`, and channel `0`.
- Added `sv_steam_stats_summary_peer_t` plus a bounded `MAX_CLIENTS` peer cache
  mirroring retail `data_e30374` as a source-side transient set.
- Added helpers to clear, deduplicate, and append pending summary peers.
- Added a summary fanout helper that measures the prepared report payload,
  sends it through `QL_Steamworks_ServerSendP2PPacket(..., 2, 0)`, logs
  sent/failed counts, and clears the pending peer cache at the match-report
  boundary.
- Registered a pending summary peer whenever a retained Steam stats session is
  created or reused.
- Updated `SV_SteamStats_ProcessMatchReport()` so the prepared payload is sent
  to pending Steam summary peers before cached `PLAYER_DEATH` events are
  cleared and before the original prepared pointer returns to the ZMQ lane.
- Strengthened the static parity gate with address-level HLIL evidence for the
  `data_e30374` walk and `SteamGameServerNetworking` call, plus source checks
  for the bounded peer cache and send-before-clear ordering.

## Remaining Gaps

- The exact retail population site for `data_e30374` remains unresolved in the
  committed corpus. The source population point is a documented inference, not
  a promoted retail rename.
- Retail suppresses the Steam summary send when the copied report is training
  or aborted. This was left open in this round and closed in
  `docs/reverse-engineering/quakelive_steam_mapping_round_520.md`.
- The qagame per-player death/report objects still omit several retail fields
  already named in round 515, including weapon, airborne, ammo, view, holdable,
  bot skill, and some achievement-adjacent details.

## Validation

Validation completed:

- `python -m pytest tests\test_platform_services.py::test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_platform_services.py -q --tb=short`
  - 134 passed.
- `python -m pytest tests\test_steamworks_harness.py -q --tb=short`
  - 128 passed.
- `python -m pytest tests\test_game_exit_rules_parity.py -q --tb=short`
  - 10 passed.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive_steam.vcxproj /m /p:Configuration=Debug /p:Platform=x86`
  - Build succeeded, 0 warnings, 0 errors.
- `git diff --check`
  - No whitespace errors; only existing LF-to-CRLF working-copy warnings.

## Confidence

Focused Steam summary P2P fanout reconstruction:

- Before: 0%
- After: 70%

Focused Steam stats match-report owner coverage:

- Before: 78%
- After: 84%

Overall Steam launch/runtime integration confidence:

- Before: 91.3%
- After: 91.4%
