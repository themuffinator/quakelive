# Quake Live Steam Mapping Round 723: Required User Auth Companion Exports

Date: 2026-06-16

## Scope

This pass rechecked the required user-auth companion exports that sit beside
the retail auth-session-ticket boundary. Round 720 pinned the required
`SteamAPI_ISteamUser_GetAuthSessionTicket` export. This round pins
`BeginAuthSession`, `CancelAuthTicket`, `EndAuthSession`, and `GetSteamID` as
the remaining required client-user auth exports in SRP's dynamic Steam runtime
loader.

Focused parity estimate: **before 87% -> after 99%** for focused required
user-auth companion export confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.24% -> 94.26%**. Repo-wide parity remains
**99%** because this pass strengthens the opt-in Steamworks harness lane,
leaves production behavior unchanged, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and symbol-map facts:

- `FUN_00460550` maps to `SteamClient_GetSteamID`.
- `FUN_004605f0` maps to `SteamClient_CancelAuthTicket`.
- `functions.csv` retains `FUN_00460550,00460550,53,0,unknown` and
  `FUN_004605f0,004605f0,27,0,unknown`.
- `imports.txt` retains `STEAM_API.DLL!SteamUser @ 0015916a`.
- `SteamAPI_ISteamUser_BeginAuthSession`,
  `SteamAPI_ISteamUser_CancelAuthTicket`,
  `SteamAPI_ISteamUser_EndAuthSession`, and
  `SteamAPI_ISteamUser_GetSteamID` are absent from the retail static import
  table, matching the reconstructed SRP dynamic-export boundary rather than
  retail import-table edges.

Observed Binary Ninja HLIL facts:

- `00460550` is the retained client SteamID wrapper.
- `004605f0` is the retained client auth-ticket cancel wrapper.
- The cancel wrapper dispatches through the `SteamUser` interface at slot
  `0x40` using the retained ticket handle.

Observed SRP source facts:

- `QL_Steamworks_LoadLibrary` treats
  `SteamAPI_ISteamUser_BeginAuthSession`,
  `SteamAPI_ISteamUser_CancelAuthTicket`,
  `SteamAPI_ISteamUser_EndAuthSession`, and
  `SteamAPI_ISteamUser_GetSteamID` as required with `QL_Steamworks_LoadSymbol`.
- Each required-export failure unloads the Steam runtime and returns `qfalse`
  before optional GameServer exports are considered.
- `QL_Steamworks_ValidateTicket` requires `BeginAuthSession` and `GetSteamID`,
  and calls `EndAuthSession` after successful validation when available.
- `QL_Steamworks_CancelAuthTicket` requires `CancelAuthTicket` before
  dispatching the retained handle to Steam.

Inference: SRP's dynamic export reconstruction should preserve the client-user
auth companion exports as required runtime capabilities. They are not optional
Web API adapters; missing any one of them should keep Steamworks uninitialized.

## Source Reconstruction

`tests/steamworks_harness.c` now carries per-export switches for
`begin_auth_session_export_available`,
`cancel_auth_ticket_export_available`, `end_auth_session_export_available`,
and `get_steam_id_export_available`. The mock dynamic loader returns `NULL`
for the corresponding required export when its switch is off, and
`QLR_SteamworksMock_PrimeState` mirrors the same guarded pointers for direct
state probes.

`tests/test_steamworks_harness.py` now includes
`test_missing_required_user_auth_companion_exports_reject_steamworks_init`,
which proves:

- the mock can hide each required client-user auth companion export
  independently;
- `QLR_Steamworks_Init` rejects the runtime for each missing export;
- `QLR_Steamworks_Request` fails with cleared ticket output values;
- `QLR_Steamworks_Validate` reports runtime unavailable instead of touching
  Steam auth state;
- `QLR_Steamworks_CancelTicket` stays cold and emits no cancel calls;
- the Web API adapter remains disabled without registering callbacks or
  issuing Web API ticket calls.

`tests/test_platform_services.py` pins the retail wrapper evidence, production
required-loader branch, harness export toggles, focused ctypes regression, and
this mapping round.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "missing_required_user_auth_companion_exports or missing_auth_session_ticket_export or validate_maps_auth_results" --tb=short`
  - `12 passed, 148 deselected in 1.56s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_required_user_auth_companion_exports_round_723 or steamworks_required_auth_session_export_round_720" --tb=short`
  - `2 passed, 260 deselected in 8.45s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `160 passed in 1.10s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `262 passed in 9.77s`
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.

Round 725 later pinned the required core Steam runtime and client interface exports, proving the Steamworks runtime stays uninitialized when any required core loader export is absent.
