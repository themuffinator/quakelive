# Quake Live Steam Mapping Round 715: Mock Loader Export Boundary Mirroring

Date: 2026-06-16

## Scope

This pass rechecked the Steamworks harness dynamic-loader boundary. Round 701
named the production `QL_STEAMWORKS_EXPORT_*` constants and preserved the
retail-first loader policy, but the harness `dlsym` mock still compared many
exports with raw string literals and only exposed several interfaces through
newer `SteamAPI_Steam*` fallback names.

Focused parity estimate: **before 90% -> after 99%** for focused Steamworks
mock loader export-boundary confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.12% -> 94.14%**. Repo-wide parity remains
**99%** because this pass clarifies test-harness loader wiring in the opt-in
Steamworks lane without changing the strict-retail Windows replacement score
and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra import-table facts:

- `imports.txt` keeps the retained retail `STEAM_API.DLL` exports:
  `SteamAPI_Init`, `SteamAPI_Shutdown`, `SteamAPI_RunCallbacks`,
  callback/call-result registration helpers, `SteamUser`, `SteamFriends`,
  `SteamApps`, `SteamUGC`, `SteamMatchmaking`, `SteamMatchmakingServers`,
  `SteamNetworking`, `SteamUtils`, `SteamUserStats`, and the GameServer
  interface exports.
- The dedicated-server bootstrap imports include
  `STEAM_API.DLL!SteamGameServer_Init @ 00159314`.
- The shutdown path imports
  `STEAM_API.DLL!SteamGameServer_Shutdown @ 001592c2`, and the frame pump keeps
  `SteamGameServer_RunCallbacks`.

Observed Binary Ninja HLIL facts:

- `0046151b` calls `SteamAPI_Init` during client Steam startup.
- `00461d63` calls `SteamAPI_RunCallbacks` in the client callback pump.
- `00465d39` calls `SteamGameServer_Shutdown`.
- `00466873` calls `SteamGameServer_RunCallbacks`.
- `00466fc1` calls `SteamGameServer_Init` before publishing dedicated server
  state and selecting the GameServer UGC owner.

Inference: the harness loader should mirror the same export-name vocabulary as
production. Exercising only `QLR_SteamworksMock_PrimeState` can hide gaps in the
dynamic loader path, so a direct `QL_Steamworks_Init` plus server-init probe is
the useful regression signal here.

## Source Reconstruction

`tests/steamworks_harness.c` now mirrors production export names with
`QLR_STEAMWORKS_EXPORT_*` constants, including:

- `QLR_STEAMWORKS_EXPORT_STEAM_API_INIT`
- `QLR_STEAMWORKS_EXPORT_STEAM_USER`
- `QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER`
- `QLR_STEAMWORKS_EXPORT_STEAM_MATCHMAKING_SERVERS`
- `QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_MATCHMAKING_SERVERS`
- `QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_INIT`
- `QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_SHUTDOWN`
- `QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_UGC`

The mock `dlsym` now resolves retail names and newer SDK aliases through those
constants instead of raw inline string literals. The mock loader also exposes
`SteamGameServer_Init`, `SteamGameServer_Shutdown`, and `SteamGameServerUGC`,
so the normal dynamic-loader path can drive server startup, shutdown, and
dedicated GameServer UGC ownership without requiring `QLR_SteamworksMock_PrimeState`.
On Windows harness builds, `QLR_LoadLibraryA`, `QLR_GetProcAddress`, and
`QLR_FreeLibrary` redirect the production loader macros to the same mock symbol
table so the test does not depend on a real Steam runtime DLL.

`tests/test_steamworks_harness.py` now includes a no-`PrimeState` runtime probe
that resets the mock state, calls `QL_Steamworks_Init`, verifies a SteamUtils
app-id read through the loader, then starts and shuts down a mock GameServer
through the dynamically resolved exports.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "dynamic_loader_resolves_retail_first_mock_exports_without_prime_state or game_server_init_uses_retail_init_signature_and_dedicated_ugc_owner" --tb=short`
  - `4 passed, 132 deselected in 1.17s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_mock_loader_export_constants_round_715 or steamworks_runtime_export_boundary_round_701 or steam_apps_mock_slot_mirroring_round_714" --tb=short`
  - `3 passed, 251 deselected in 0.16s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `136 passed in 1.08s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `253 passed, 1 failed in 10.88s`; the failure is the pre-existing Round
    698 gate referencing missing
    `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
