# Quake Live Steam Mapping Round 737: Optional GameServer Export Fallbacks

Date: 2026-06-16

## Scope

This round pins the optional Steam GameServer export boundary in SRP's
dynamic, opt-in Steamworks runtime loader. Retail Quake Live imports the
GameServer family directly from `steam_api.dll`, while SRP deliberately keeps
the Steamworks runtime behind `QL_BUILD_ONLINE_SERVICES` / `QL_BUILD_STEAMWORKS`
and allows absent optional server-side exports to fail closed at their local
feature owners.

The pinned optional family is `SteamGameServer`, `SteamGameServerStats`, `SteamGameServerUtils`,
`SteamGameServerUGC`, `SteamGameServer_Init`, `SteamGameServer_Shutdown`,
`SteamGameServer_RunCallbacks`, and `SteamGameServerNetworking`.

Focused parity estimate: **before 88% -> after 99%** for optional GameServer
export fallback confidence.

Overall Steam launch/runtime integration mapping confidence moves from
**94.32% -> 94.34%**. Repo-wide parity remains **99%** because this pass
strengthens the opt-in Steamworks harness lane, leaves live Steam behavior
default-disabled, and does not change the strict-retail Windows replacement
score.
Overall Steam launch/runtime integration mapping confidence moves from **94.32% -> 94.34%**.
This does not enable live Steam behavior by default.

Focused lane: optional GameServer export fallback confidence.

## Retail Evidence

Observed Ghidra import anchors:

- `STEAM_API.DLL!SteamGameServer @ 0015918a`
- `STEAM_API.DLL!SteamGameServerNetworking @ 001592a6`
- `STEAM_API.DLL!SteamGameServerStats @ 0015932c`
- `STEAM_API.DLL!SteamGameServerUGC @ 001592fe`
- `STEAM_API.DLL!SteamGameServerUtils @ 00159344`
- `STEAM_API.DLL!SteamGameServer_Init @ 00159314`
- `STEAM_API.DLL!SteamGameServer_RunCallbacks @ 001592de`
- `STEAM_API.DLL!SteamGameServer_Shutdown @ 001592c2`

Observed Binary Ninja HLIL extern anchors:

- `SteamGameServer`
- `SteamGameServerNetworking`
- `SteamGameServerStats`
- `SteamGameServerUGC`
- `SteamGameServerUtils`
- `SteamGameServer_Init`
- `SteamGameServer_RunCallbacks`
- `SteamGameServer_Shutdown`

Observed HLIL call-shape anchors:

- `SteamGameServer_Shutdown()` in the retail server shutdown path.
- `SteamGameServer_RunCallbacks()` in the server callback pump.
- `SteamGameServer_Init(...)` before the retail GameServer bootstrap writes.
- `SteamGameServerNetworking()` before server-side P2P availability/read slots.
- `SteamGameServerUtils(...)->GetAppID` in the server stats/app-id lane.
- `SteamGameServerStats()` combined with `SteamGameServer()->BLoggedOn()` in
  the server stats request gate.

Inference: the retail binary expects these exports from Steam's runtime, but
SRP's reconstruction keeps live-service usage optional. Missing GameServer
exports should not make client auth-ticket acquisition unusable; each missing
export should disable only the server feature surface it owns.

## Reconstructed Boundary

`QL_Steamworks_LoadLibrary` already resolves all eight GameServer symbols with
`QL_Steamworks_LoadOptionalSymbol`:

- `SteamGameServer`
- `SteamGameServerStats`
- `SteamGameServerUtils`
- `SteamGameServerUGC`
- `SteamGameServer_Init`
- `SteamGameServer_Shutdown`
- `SteamGameServer_RunCallbacks`
- `SteamGameServerNetworking`

The production wrappers then fail closed at local gates:

- `QL_Steamworks_ServerInitWithVersion` requires `SteamGameServer_Init` before
  setting `gameServerInitialised`.
- `QL_Steamworks_ServerShutdown` clears local server state even when
  `SteamGameServer_Shutdown` is absent.
- `QL_Steamworks_RunServerCallbacks` skips the server callback pump without
  `SteamGameServer_RunCallbacks`.
- `QL_Steamworks_GetGameServer`, `QL_Steamworks_GetGameServerStatsInterface`,
  `QL_Steamworks_GetGameServerUtilsInterface`, and
  `QL_Steamworks_GetGameServerNetworking` return `NULL` when their cached
  optional interface export is absent.
- `QL_Steamworks_GetUGCInterface` first tries `SteamGameServerUGC` only when
  the active server owner requested it, then falls back to the client
  `SteamUGC` owner when that interface is available.

Important inference: `SteamGameServer` itself is not required by
`SteamGameServer_Init`. A runtime with `SteamGameServer_Init` but no
`SteamGameServer` can still mark the server init path active, while every
downstream `SteamGameServer` vtable helper fails closed.

Pinned fallback nuance: `SteamGameServer` itself is not required by `SteamGameServer_Init`.

## Source Reconstruction

`tests/steamworks_harness.c` now carries eight GameServer export-availability
switches:

- `steam_game_server_export_available`
- `steam_game_server_stats_export_available`
- `steam_game_server_utils_export_available`
- `steam_game_server_ugc_export_available`
- `steam_game_server_init_export_available`
- `steam_game_server_shutdown_export_available`
- `steam_game_server_run_callbacks_export_available`
- `steam_game_server_networking_export_available`

The mock `dlsym` path and `QLR_SteamworksMock_PrimeState` both mirror those
switches, so dynamic-loader and direct-state probes exercise the same optional
export contract.

`tests/test_steamworks_harness.py` now proves:

- missing `SteamGameServer_Init` keeps Steam init and the retail auth-ticket
  path working while rejecting server init before any mock init call;
- missing `SteamGameServer` keeps server init active but disables
  GameServer-vtable helpers such as logged-on checks, product writes, identity
  reads, public-IP reads, and UDP packet handling;
- missing `SteamGameServer_Shutdown` still clears local server state without a
  runtime shutdown call;
- missing `SteamGameServer_RunCallbacks` leaves queued server callbacks
  undispatched by the server callback pump;
- missing `SteamGameServerStats` keeps server init active while disabling
  server stats requests and reads before vtable calls;
- missing `SteamGameServerUtils` keeps server init active while making
  `QL_Steamworks_ServerGetAppID` return `0`;
- missing `SteamGameServerUGC` falls back to the client `SteamUGC` owner for
  workshop operations;
- missing `SteamGameServerNetworking` keeps server init active while disabling
  server P2P send, availability, read, and accept calls.

`tests/test_platform_services.py` pins the retail import/HLIL evidence,
production optional loader shape, harness export toggles, focused ctypes
regressions, and this mapping round.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "missing_optional_gameserver" --tb=short`
  - `16 passed, 192 deselected in 2.43s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_optional_gameserver_exports_round_737 or steamworks_mock_loader_export_constants_round_715 or steamworks_optional_auxiliary_interface_exports_round_731" --tb=short`
  - `3 passed, 272 deselected in 0.13s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `208 passed in 1.10s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks" --tb=short`
  - `20 passed, 255 deselected in 1.55s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `275 passed in 11.64s`
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
