# Quake Live Steam Mapping Round 725: Required Core Runtime Exports

Date: 2026-06-16

## Scope

This pass rechecked the required core Steam runtime and client interface export
boundary in SRP's dynamic Steamworks loader. Rounds 720 and 723 pinned the
required auth-ticket and user-auth exports. This round pins `SteamAPI_Init`,
`SteamAPI_Shutdown`, and `SteamAPI_RunCallbacks`, plus `SteamUser`,
`SteamFriends`, `SteamMatchmaking`, `SteamApps`, and `SteamUGC`, as required
client-runtime capabilities.

Focused parity estimate: **before 87% -> after 99%** for focused required core
Steam runtime export confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.26% -> 94.28%**. Repo-wide parity remains
**99%** because this pass strengthens the opt-in Steamworks harness lane,
leaves production behavior unchanged, and does not enable live Steam behavior by default.

The required core runtime trio is `SteamAPI_Init`, `SteamAPI_Shutdown`, and `SteamAPI_RunCallbacks`.
The required client interface group is `SteamUser`, `SteamFriends`, `SteamMatchmaking`, `SteamApps`, and `SteamUGC`.

## Evidence

Observed Ghidra import-table facts:

- `imports.txt` retains `SteamAPI_Init`, `SteamAPI_RunCallbacks`, and
  `SteamAPI_Shutdown`.
- `imports.txt` retains the required client interfaces `SteamUser`,
  `SteamFriends`, `SteamMatchmaking`, `SteamApps`, and `SteamUGC`.

Observed Binary Ninja HLIL facts:

- `0046151b` calls `SteamAPI_Init()` during client Steam startup.
- `00461d63` pumps client callbacks through `SteamAPI_RunCallbacks()`.
- `00460540` tail-calls `SteamAPI_Shutdown()`.
- The HLIL extern table retains the core runtime and client interface symbols.

Observed SRP source facts:

- `QL_Steamworks_LoadLibrary` treats `SteamAPI_Init`, `SteamAPI_Shutdown`, and
  `SteamAPI_RunCallbacks` as required `QL_Steamworks_LoadSymbol` exports.
- `QL_Steamworks_LoadLibrary` treats `SteamUser`, `SteamFriends`,
  `SteamMatchmaking`, `SteamApps`, and `SteamUGC` as required
  `QL_Steamworks_LoadSymbolAlias` exports, preserving both retail and SDK
  spellings.
- Optional callback, auxiliary client-interface, and GameServer exports remain
  outside this required core boundary.

Inference: missing any required core runtime export should reject the loaded
Steam runtime before auth-ticket, Web API, social, lobby, app, or workshop
helpers can touch Steam state.

## Source Reconstruction

`tests/steamworks_harness.c` now carries per-export switches for
`steam_api_init_export_available`, `steam_api_shutdown_export_available`,
`steam_api_run_callbacks_export_available`, `steam_user_export_available`,
`steam_friends_export_available`, `steam_matchmaking_export_available`,
`steam_apps_export_available`, and `steam_ugc_export_available`. The mock
dynamic loader returns `NULL` for the corresponding required export when its
switch is off, and `QLR_SteamworksMock_PrimeState` mirrors the same guarded
pointers for direct state probes.

`tests/test_steamworks_harness.py` now includes
`test_missing_required_core_runtime_exports_reject_steamworks_init`, which
proves:

- the mock can hide each required core runtime or client interface export
  independently;
- `QLR_Steamworks_Init` rejects the runtime for each missing export;
- `QLR_Steamworks_Request` fails with cleared ticket output values;
- `QLR_Steamworks_Validate` reports runtime unavailable instead of touching
  Steam auth state;
- `QLR_Steamworks_CancelTicket` stays cold and emits no cancel calls;
- the Web API adapter remains disabled without registering callbacks or
  issuing Web API ticket calls.

`tests/test_platform_services.py` pins the retail import evidence, HLIL call
sites, production required-loader branch, harness export toggles, focused
ctypes regression, and this mapping round.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "missing_required_core_runtime_exports or missing_required_user_auth_companion_exports or request_produces_expected_ticket" --tb=short`
  - `26 passed, 150 deselected in 2.10s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_required_core_runtime_exports_round_725 or steamworks_required_user_auth_companion_exports_round_723" --tb=short`
  - `2 passed, 263 deselected in 0.11s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `176 passed in 1.27s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `265 passed in 9.77s`
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
