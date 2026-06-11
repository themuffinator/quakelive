# Quake Live Steam Mapping Round 500: GSStatsStored Validation Refresh

## Scope

This round maps and reconstructs the `GSStatsStored_t` validation-warning path
used by retail Quake Live after `SteamGameServerStats()->StoreUserStats`.
Retail result `8` does not issue another `RequestUserStats` call. Instead, it
routes directly into the same local stats-received refresh path used by
`GSStatsReceived_t` success.

This is part of Steam launch/runtime integration because dedicated-server stat
storage has to preserve Steam's partial-validation behavior without creating an
extra backend request loop.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/server/sv_client.c`
- `tests/test_platform_services.py`

Observed facts:

- Retail callback owner `sub_467360` handles `GSStatsStored_t`.
- `0046737e` handles result `1` as store success.
- `004673a1` sends all results other than `8` through the failure log path.
- Result `8` logs the partial-validation warning at `004673a8`.
- Retail writes a synthetic result value `1` at `004673c5` and then calls
  `sub_4671d0(arg1, &var_94)` at `004673d5`, reusing the stats-received
  success refresh path.

## Reconstruction

Implemented changes:

- Factored the successful received-values refresh into
  `SV_SteamStats_PrimeReceivedValues()`.
- Routed `SV_SteamServerGSStatsReceivedCallback()` result `1` through the new
  helper.
- Changed `SV_SteamServerGSStatsStoredCallback()` result `8` to call the same
  local received-values helper instead of clearing `requestIssued` and issuing
  a new `SV_SteamStats_RequestCurrentValues()` call.
- Strengthened static parity coverage for the retail `sub_467360` address
  sequence and for the source rule that result `8` warms locally without a new
  request.

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

No game launch was performed. The retail HLIL branch, source reconstruction,
static parity coverage, harness run, and x86 build were enough for this pass.

## Confidence

High confidence for the result `8` branch:

- The HLIL call to `sub_4671d0` with synthetic result `1` maps directly to the
  shared `SV_SteamStats_PrimeReceivedValues()` helper.

Medium confidence for the full store lifecycle:

- Store success/failure/partial-validation control flow is now pinned, but
  exact retail achievement-table bookkeeping remains an adjacent mapped-only
  area.

## Parity Estimate

Focused GSStatsStored validation-refresh path:

- Before: 84%
- After: 97%

Overall Steam launch/runtime integration:

- Before: 90.1%
- After: 90.2%
