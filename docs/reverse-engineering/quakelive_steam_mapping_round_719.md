# Quake Live Steam Mapping Round 719: Optional Web API Auth Ticket Export

Date: 2026-06-16

## Scope

This pass rechecked the auth-ticket API boundary between the retail
`GetAuthSessionTicket` path and SRP's opt-in Web API auth-ticket adapter.
Rounds 716 through 718 pinned Web API callback failure, lifecycle handoff, and
sequential reuse. This round pins the loader boundary when the newer
`SteamAPI_ISteamUser_GetAuthTicketForWebApi` export is absent.

Focused parity estimate: **before 86% -> after 99%** for focused optional Web
API auth-ticket export confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.20% -> 94.22%**. Repo-wide parity remains
**99%** because this pass strengthens the opt-in Steamworks harness lane,
leaves production behavior unchanged, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra corpus facts:

- `metadata.txt` identifies the owning retail binary as `quakelive_steam.exe`
  with `351` imports.
- `imports.txt` retains `STEAM_API.DLL!SteamAPI_RegisterCallback @ 00159248`
  and `STEAM_API.DLL!SteamAPI_RunCallbacks @ 00159274`.
- `SteamAPI_ISteamUser_GetAuthTicketForWebApi` is absent from the retail static import table.

Observed Binary Ninja HLIL facts:

- `quakelive_steam.exe_hlil_part19.txt` retains extern rows for
  `SteamAPI_RegisterCallback` and `SteamAPI_RunCallbacks`.
- The retail HLIL corpus does not expose a static
  `SteamAPI_ISteamUser_GetAuthTicketForWebApi` import edge.

Observed SRP source facts:

- `QL_Steamworks_LoadLibrary` treats
  `SteamAPI_ISteamUser_GetAuthSessionTicket` as required with
  `QL_Steamworks_LoadSymbol`.
- The newer `SteamAPI_ISteamUser_GetAuthTicketForWebApi` export is loaded with
  `QL_Steamworks_LoadOptionalSymbol`.
- `QL_Steamworks_HasWebApiAuthTicketAdapter` requires the optional Web API
  ticket export plus callback registration and callback pumping exports.
- `QL_Steamworks_RequestWebApiAuthTicket` returns false before registering or
  pumping a Web API callback when the optional export is missing.
- `QL_Steamworks_RequestAuthTicket` still calls the required retail
  `GetAuthSessionTicket` entry point.

Inference: the Web API ticket helper is a deliberately optional SRP adapter.
Missing that modern export should disable only the Web API wrapper, while the
retail `GetAuthSessionTicket` auth-ticket path remains usable.

## Source Reconstruction

`tests/steamworks_harness.c` now carries a
`web_api_ticket_export_available` switch. The mock dynamic loader returns
`NULL` for `SteamAPI_ISteamUser_GetAuthTicketForWebApi` when that switch is
off, and `QLR_SteamworksMock_PrimeState` mirrors the same optional pointer
state for direct source-level probes.

`tests/test_steamworks_harness.py` now includes
`test_missing_web_api_ticket_export_keeps_retail_auth_session_ticket_path`,
which proves:

- the mock can hide the modern Web API ticket export;
- `QLR_Steamworks_HasWebApiAuthTicketAdapter` reports false;
- `QLR_Steamworks_RequestWebApi` fails without registering callbacks, pumping
  Web API ticket calls, or leaving stale output values;
- the normal `QLR_Steamworks_Request` wrapper still returns the retail
  `GetAuthSessionTicket` mock payload `12345678` and handle `1`;
- resetting the mock restores the default export availability for later tests.

`tests/test_platform_services.py` pins the retail import evidence, production
required-versus-optional loader shape, harness export toggle, focused ctypes
regression, and this mapping round.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "missing_web_api_ticket_export or web_api_ticket_callback_is_reused_across_sequential_requests or web_api_auth_ticket_adapter" --tb=short`
  - `14 passed, 136 deselected in 2.04s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_web_api_optional_export_round_719 or steamworks_web_api_callback_reuse_round_718" --tb=short`
  - `2 passed, 256 deselected in 4.23s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `150 passed in 1.02s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `257 passed, 1 failed in 11.22s`; the failure is the pre-existing Round
    698 gate referencing missing
    `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.

Round 720 later pinned the required retail auth-session-ticket export boundary,
proving the Steamworks runtime stays uninitialized when GetAuthSessionTicket is
absent.

Round 729 later pinned the optional callback and call-result export fallbacks
that keep the Web API adapter disabled while leaving the retail auth-ticket
path usable.
