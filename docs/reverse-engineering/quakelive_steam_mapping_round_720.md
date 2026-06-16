# Quake Live Steam Mapping Round 720: Required Auth Session Ticket Export

Date: 2026-06-16

## Scope

This pass rechecked the required retail auth-session-ticket export boundary.
Round 719 proved the newer Web API ticket adapter can be absent without
breaking the retail ticket path. This round pins the inverse: if the required
`SteamAPI_ISteamUser_GetAuthSessionTicket` export is absent from SRP's loaded
Steam runtime, Steamworks initialization must fail cleanly and both auth-ticket
wrappers must stay cold.

Focused parity estimate: **before 87% -> after 99%** for focused required
auth-session-ticket export confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.22% -> 94.24%**. Repo-wide parity remains
**99%** because this pass strengthens the opt-in Steamworks harness lane,
leaves production behavior unchanged, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and symbol-map facts:

- `FUN_004605c0` maps to `SteamClient_GetAuthSessionTicket` in
  `references/analysis/quakelive_symbol_aliases.json`.
- `functions.csv` retains `FUN_004605c0,004605c0,43,0,unknown`.
- `imports.txt` retains `STEAM_API.DLL!SteamUser @ 0015916a`.
- `SteamAPI_ISteamUser_GetAuthSessionTicket` is absent from the retail static
  import table, matching the reconstructed SRP dynamic-export boundary rather
  than a retail import-table edge.

Observed Binary Ninja HLIL facts:

- `004605c0` is the retained auth-session-ticket wrapper.
- The wrapper calls through the `SteamUser` interface at slot `0x34`.
- Downstream retail paths call `sub_4605c0` when building auth ticket payloads.

Observed SRP source facts:

- `QL_Steamworks_LoadLibrary` treats
  `SteamAPI_ISteamUser_GetAuthSessionTicket` as required with
  `QL_Steamworks_LoadSymbol`.
- Failure to resolve that required export unloads the mock Steam runtime and
  returns `qfalse`.
- `QL_Steamworks_RequestAuthTicket` also guards against a missing
  `state.GetAuthSessionTicket` pointer before calling the export.
- `QL_Steamworks_RequestWebApiAuthTicket` depends on successful
  `QL_Steamworks_Init`, so a missing required retail ticket export also keeps
  the optional Web API adapter disabled.

Inference: SRP's dynamic export reconstruction should preserve the retail
auth-session-ticket path as a required runtime capability. The Web API adapter
is optional, but the retail `GetAuthSessionTicket` path is not.

## Source Reconstruction

`tests/steamworks_harness.c` now carries an
`auth_session_ticket_export_available` switch. The mock dynamic loader returns
`NULL` for `SteamAPI_ISteamUser_GetAuthSessionTicket` when that switch is off,
and `QLR_SteamworksMock_PrimeState` mirrors the same guarded pointer for direct
state probes.

`tests/test_steamworks_harness.py` now includes
`test_missing_auth_session_ticket_export_rejects_steamworks_init`, which
proves:

- the mock can hide the required retail auth-session-ticket export;
- `QLR_Steamworks_Init` rejects the runtime through the dynamic loader path;
- `QLR_Steamworks_Request` fails with cleared ticket output values;
- `QLR_Steamworks_HasWebApiAuthTicketAdapter` remains false;
- `QLR_Steamworks_RequestWebApi` fails without registering callbacks or
  issuing Web API ticket calls;
- resetting the mock restores the required export for later tests.

`tests/test_platform_services.py` pins the retail wrapper evidence, production
required-loader branch, harness export toggle, focused ctypes regression, and
this mapping round.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "missing_auth_session_ticket_export or missing_web_api_ticket_export or request_produces_expected_ticket" --tb=short`
  - `6 passed, 146 deselected in 5.03s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_required_auth_session_export_round_720 or steamworks_web_api_optional_export_round_719" --tb=short`
  - `2 passed, 258 deselected in 4.65s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `152 passed in 0.99s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `260 passed in 9.85s`
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.

Round 723 later pinned the remaining required user-auth companion exports,
proving the Steamworks runtime stays uninitialized when BeginAuthSession,
CancelAuthTicket, EndAuthSession, or GetSteamID is absent.
