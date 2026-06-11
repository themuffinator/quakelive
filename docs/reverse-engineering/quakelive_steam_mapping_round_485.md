# Quake Live Steam Mapping Round 485: Steamworks Loader Import Contract

## Scope

This round maps the Steamworks loader and launch-contract boundary. The pass
focuses on retail's direct `STEAM_API.DLL` import surface, SRP's dynamic loader
equivalent, the split between required client exports and optional callback /
GameServer exports, and the absence of a Steam self-relaunch path.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `src/common/platform/platform_steamworks.c`

Observed facts:

- Retail imports the core Steam client exports directly from `STEAM_API.DLL`:
  `SteamAPI_Init`, `SteamAPI_RunCallbacks`, `SteamAPI_Shutdown`,
  `SteamApps`, `SteamFriends`, `SteamMatchmaking`, `SteamUGC`, `SteamUser`,
  and `SteamUtils`.
- Retail imports the callback registration exports:
  `SteamAPI_RegisterCallback`, `SteamAPI_UnregisterCallback`,
  `SteamAPI_RegisterCallResult`, and `SteamAPI_UnregisterCallResult`.
- Retail imports the server-side Steam surface:
  `SteamGameServer`, `SteamGameServerNetworking`, `SteamGameServerStats`,
  `SteamGameServerUGC`, `SteamGameServerUtils`, `SteamGameServer_Init`,
  `SteamGameServer_RunCallbacks`, and `SteamGameServer_Shutdown`.
- Retail import tables and HLIL import symbols do not contain
  `SteamAPI_RestartAppIfNecessary`.
- The observed launch contract is therefore "Steam launches or already hosts
  the process" rather than "the executable detects and relaunches itself via
  Steam".

## Source Reconstruction

Implemented source-side changes:

- Added
  `test_platform_steamworks_loader_reconstructs_retail_import_surface_and_launch_contract`
  to `tests/test_platform_services.py`.
- Pinned the full retail Steam import surface against Ghidra `imports.txt`.
- Pinned representative HLIL import-table symbols from part 06.
- Added negative assertions that `SteamAPI_RestartAppIfNecessary` is absent
  from the retail import evidence and from SRP's Steamworks loader.
- Added source assertions for the Windows and non-Windows Steam runtime
  candidate names:
  - `steam_api.dll`
  - `steam_api64.dll`
  - `libsteam_api.so`
- Added source assertions that the loader requires:
  - `SteamAPI_Init`
  - `SteamAPI_Shutdown`
  - `SteamAPI_RunCallbacks`
  - `SteamUser`
  - `SteamFriends`
  - `SteamMatchmaking`
  - `SteamApps`
  - `SteamUGC`
  - the retained `SteamAPI_ISteamUser_*` auth and SteamID helpers
- Added source assertions that callback registration, user-stats/utils,
  server-browser, and GameServer exports remain optional, matching SRP's
  compatibility fallback policy.
- Added source assertions that retail export names are tried before newer SDK
  aliases.
- Added source assertions that `QL_Steamworks_Init` only sets the retained
  initialized flag after `SteamAPI_Init` succeeds.
- Added disabled-build stub coverage proving default builds do not load Steam.

No C source edit was needed. The current dynamic loader already matches the
retail import contract while preserving SRP's default-disabled online-services
policy.

## Validation

Focused validation passed:

- `python -m pytest tests/test_platform_services.py::test_platform_steamworks_loader_reconstructs_retail_import_surface_and_launch_contract tests/test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface -q --tb=short`

## Parity Estimate

Scoped Steamworks loader/import launch contract:

- Before: 88%
- After: 97%

Overall Steam launch/runtime integration:

- Before: 87%
- After: 88%
