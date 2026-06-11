# Quake Live Steam Mapping Round 499: GSStatsReceived Session Warmup

## Scope

This round maps and reconstructs the server-owned `GSStatsReceived_t` path used
after `SteamGameServerStats()->RequestUserStats`. Retail does not treat a
successful request call as proof that stats are ready; the backend-ready state
is established by the stats-received callback when the result is `1`.

This is part of Steam launch/runtime integration because dedicated-server stat
publication depends on preserving the cold request state until Steam confirms
that the player stats payload is available.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- Retail callback owner `sub_4671d0` handles `GSStatsReceived_t`.
- `004671ee` branches to the failure path when the result is not `1`.
- On success, retail logs the received-stats path and walks the mapped stat
  descriptor array.
- Integer stats are fetched through `SteamGameServerStats` vtable slot `0x08`.
- Float and average-rate stats are fetched through vtable slot `0x04`.
- Retail sets the ready flag at `00467283` after the success path finishes.

## Reconstruction

Implemented changes:

- Changed `SV_SteamStats_RequestCurrentValues()` so request issuance clears and
  then sets only `requestIssued`; it no longer marks `backendAvailable`.
- Added cold-state guards to stat and achievement value loading so direct
  `SteamGameServerStats` reads wait for a received callback.
- Made server reconnect requery explicitly cold the session backend before
  issuing a new request.
- Updated `SV_SteamServerGSStatsReceivedCallback()` so result `1` warms the
  session, primes mapped stat fields through `SV_SteamStats_LoadFieldValue()`,
  and failed results clear both `backendAvailable` and `requestIssued`.
- Strengthened static parity coverage with the retail HLIL callback addresses,
  vtable slots, ready-flag write, and source-order assertions for the cold and
  warm paths.

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
- `git diff --check -- src/code/server/sv_client.c tests/test_platform_services.py`
  - No whitespace errors; Git reported CRLF normalization warnings for tracked
    text files.

No game launch was performed. Static retail evidence, focused static parity
coverage, the Steamworks harness, and the x86 build were sufficient for this
session-state reconstruction.

## Confidence

High confidence for the request cold-state correction:

- Retail HLIL and SRP source now agree that a request call is distinct from a
  received successful stats payload.

Medium-high confidence for success-path stat priming:

- The callback now follows the retail success shape and uses the already mapped
  GameServerStats value slots. There is still residual uncertainty around the
  exact retail achievement array bookkeeping in the same callback region.

## Parity Estimate

Focused GameServer stats received-session warmup:

- Before: 83%
- After: 96%

Overall Steam launch/runtime integration:

- Before: 90.0%
- After: 90.1%
