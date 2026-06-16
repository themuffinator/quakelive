# Quake Live Steam Mapping Round 701: Steamworks Runtime Export Boundary Constants

Date: 2026-06-16

## Scope

This pass rechecked the Steamworks DLL/runtime export boundary used by
`QL_Steamworks_LoadLibrary`. The reconstruction goal was to replace inline
production export-name literals with named constants while preserving the
existing loader policy: required client startup/auth exports must resolve,
optional callback/server exports may remain unavailable, and retail export
names are tried before newer `SteamAPI_*` interface aliases.

Focused parity estimate: **before 88% -> after 99%** for focused Steamworks
runtime export-boundary source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.84% -> 93.86%**.
Repo-wide parity remains **99%** because this pass clarifies the opt-in
Steamworks runtime wiring without changing the strict-retail Windows
replacement score and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra import-table facts:

- `STEAM_API.DLL` imports include `SteamAPI_Init`, `SteamAPI_Shutdown`,
  `SteamAPI_RunCallbacks`, callback/call-result registration helpers,
  `SteamUser`, `SteamFriends`, `SteamApps`, `SteamUGC`, `SteamMatchmaking`,
  `SteamMatchmakingServers`, `SteamNetworking`, `SteamUtils`,
  `SteamUserStats`, and the GameServer interface exports.
- `functions.csv` contains the small imported `SteamAPI_Shutdown` tailcall row
  at `00460540`.
- `references/analysis/quakelive_symbol_aliases.json` maps `sub_460540` to
  `SteamAPI_Shutdown`.

Observed Binary Ninja HLIL anchors:

- `0046151b` calls `SteamAPI_Init` during `SteamClient_Init`.
- `00461d63` calls `SteamAPI_RunCallbacks` during the client frame pump.
- `00460e25` and `00460e4e` call `SteamAPI_UnregisterCallResult` and
  `SteamAPI_RegisterCallResult` around the UGC query call-result object.
- `004613f5` calls `SteamAPI_RegisterCallback` for client callback setup.
- `00465d39`, `00466873`, and `00466fc1` call `SteamGameServer_Shutdown`,
  `SteamGameServer_RunCallbacks`, and `SteamGameServer_Init`.

Inference: retail Quake Live links directly against the 2010-era
`STEAM_API.DLL` export names. SRP's dynamic loader should keep those retail
names as the primary contract while allowing newer `SteamAPI_Steam*` aliases
such as `SteamAPI_SteamUser` only as compatibility fallbacks when loading a
different Steamworks SDK runtime.

## Source Reconstruction

The production loader now names the runtime export contract with
`QL_STEAMWORKS_EXPORT_*` constants, including:

- `QL_STEAMWORKS_EXPORT_STEAM_API_INIT`
- `QL_STEAMWORKS_EXPORT_STEAM_API_SHUTDOWN`
- `QL_STEAMWORKS_EXPORT_STEAM_API_RUN_CALLBACKS`
- `QL_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALLBACK`
- `QL_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALL_RESULT`
- `QL_STEAMWORKS_EXPORT_STEAM_USER`
- `QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER`
- `QL_STEAMWORKS_EXPORT_STEAM_FRIENDS`
- `QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_FRIENDS`
- `QL_STEAMWORKS_EXPORT_STEAM_APPS`
- `QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_APPS`
- `QL_STEAMWORKS_EXPORT_STEAM_UGC`
- `QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_UGC`
- `QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_AUTH_SESSION_TICKET`
- `QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_BEGIN_AUTH_SESSION`
- `QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_END_AUTH_SESSION`
- `QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER`
- `QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_INIT`
- `QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_RUN_CALLBACKS`

`QL_Steamworks_LoadSymbolAlias` and
`QL_Steamworks_LoadOptionalSymbolAlias` still try the retail name before the
newer SDK alias. `SteamAPI_RestartAppIfNecessary` remains absent because it is
not present in the retail import table and would change startup ownership.
Round 715 later mirrored these export constants in the Steamworks harness loader so dynamic-loader tests exercise the same retail-first vocabulary.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steamworks_runtime_export_boundary_round_701 or platform_steamworks_loader_reconstructs_retail_import_surface_and_launch_contract or platform_steamworks_reconstructs_retail_callback_bundle_registration_surface or steamworks_modern_adapter_gaps_stay_explicit_until_owned or server_game_server_wrappers_reconstruct_mapped_server_slots or steam_gameserver_auth_session_wrapper_guards_track_round_628" --tb=short` - 6 passed, 234 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 239 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
