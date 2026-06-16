# Quake Live Steam Mapping Round 731: Optional Auxiliary Interface Exports

Date: 2026-06-16

## Scope

This pass rechecked the auxiliary client Steam interface exports that retail
imports directly but SRP resolves through optional dynamic-loader aliases:
`SteamUtils`, `SteamUserStats`, `SteamNetworking`, and
`SteamMatchmakingServers`. These interfaces own app/country helpers, client
stats readback and reset, legacy P2P packet helpers, and the native server
browser. They are useful when present, but they are not required for SRP's
retail auth-ticket path or for Steamworks runtime initialisation.

Focused parity estimate: **before 88% -> after 99%** for focused optional
auxiliary interface export fallback confidence.
Overall Steam launch/runtime integration mapping confidence moves from **94.30% -> 94.32%**.
Repo-wide parity remains **99%** because this pass strengthens the opt-in
Steamworks harness lane, leaves live service use default-disabled, and does
not change the strict-retail Windows replacement score.
This pass does not change the strict-retail Windows replacement score.

## Evidence

Observed Ghidra corpus facts:

- `imports.txt` retains `STEAM_API.DLL!SteamUtils @ 0015914c`,
  `STEAM_API.DLL!SteamUserStats @ 0015919c`,
  `STEAM_API.DLL!SteamNetworking @ 001591ba`, and
  `STEAM_API.DLL!SteamMatchmakingServers @ 0015928c`.

Observed Binary Ninja HLIL facts:

- `quakelive_steam.exe_hlil_part19.txt` retains extern rows for all four
  auxiliary interfaces.
- `quakelive_steam.exe_hlil_part02.txt` shows `SteamUtils` app-id and country
  access, `SteamUserStats` reset/readback access, legacy `SteamNetworking`
  packet probes, and `SteamMatchmakingServers` list/detail request calls.

Observed SRP source facts:

- `QL_Steamworks_LoadLibrary` resolves all four interfaces with
  `QL_Steamworks_LoadOptionalSymbolAlias`, trying the retail export name before
  the newer SDK alias.
- `QL_Steamworks_GetUtilsInterface`, `QL_Steamworks_GetUserStatsInterface`,
  `QL_Steamworks_GetNetworkingInterface`, and
  `QL_Steamworks_GetServerBrowserInterface` fail closed when their cached
  optional export is unavailable.
- `QL_Steamworks_GetAppID` returns `0` and `QL_Steamworks_GetIPCountry` returns
  false without `SteamUtils`.
- `QL_Steamworks_ClearStats`, `QL_Steamworks_RequestUserStats`, and stats
  readback helpers return false without `SteamUserStats`.
- Legacy client P2P wrappers return false without `SteamNetworking`; failed
  read projections clear the exported SteamID while preserving the untouched
  packet-size value.
- `QL_Steamworks_HasServerBrowserInterface`,
  `QL_Steamworks_RequestServerList`, and detail query helpers fail without
  `SteamMatchmakingServers`.

Inference: these interfaces are retail-observed but intentionally optional at
SRP's runtime boundary. Missing auxiliary interfaces should disable only the
feature surfaces they own while leaving `QLR_Steamworks_Init` and the retail
`GetAuthSessionTicket` wrapper usable.

## Source Reconstruction

`tests/steamworks_harness.c` now carries four auxiliary interface
export-availability switches:

- `steam_utils_export_available`
- `steam_user_stats_export_available`
- `steam_networking_export_available`
- `steam_matchmaking_servers_export_available`

The mock `dlsym` path and `QLR_SteamworksMock_PrimeState` both mirror those
switches, so dynamic-loader and direct-state probes exercise the same optional
export contract.

`tests/test_steamworks_harness.py` now proves:

- missing `SteamUtils` keeps Steam init and the retail auth-ticket path working
  while disabling app-id and IP-country helper calls;
- missing `SteamUserStats` keeps the auth-ticket path working while disabling
  stats reset, request, and readback vtable calls;
- missing `SteamNetworking` keeps the auth-ticket path working while disabling
  legacy client P2P send, availability, read, and accept vtable calls;
- missing `SteamMatchmakingServers` keeps the auth-ticket path working while
  disabling native server-list and detail-query requests.

`tests/test_platform_services.py` pins the retail import/HLIL evidence,
production optional-alias loader shape, harness export toggles, focused ctypes
regressions, and this mapping round.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "missing_optional_steamutils or missing_optional_steamuserstats or missing_optional_steamnetworking or missing_optional_steammatchmakingservers" --tb=short`
  - `8 passed, 184 deselected in 1.61s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_optional_auxiliary_interface_exports_round_731 or steamworks_mock_loader_export_constants_round_715 or steamworks_optional_callback_export_fallbacks_round_729" --tb=short`
  - `3 passed, 268 deselected in 0.13s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `192 passed in 0.98s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks" --tb=short`
  - `19 passed, 252 deselected in 1.23s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `271 passed in 12.80s`
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.

Round 737 later pinned the optional GameServer export fallbacks, extending this
same optional-export harness pattern to the server-side Steam runtime family.
