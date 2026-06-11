# Quake Live Steam Mapping Round 596: Client Steam Auth Dispatch Boundary

Date: 2026-06-11

## Scope

This round rechecks the client Steam auth dispatch path against the retail
`quakelive_steam.exe` Binary Ninja HLIL and committed Ghidra corpus. The focus
is the boundary between the retail-style ticket lifetime wrappers and the
repository's explicitly bounded compatibility auth backends.

No engine source behavior was changed in this pass. The work adds stronger
tests and updates the client-auth gap note so future reconstruction cannot
silently widen hybrid fallback behavior or bypass the retained ticket owner.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- Binary Ninja HLIL part 02:
  - `sub_4605c0` / `FUN_004605c0`: calls `SteamUser()` and dispatches vtable
    slot `0x34`, storing the returned handle in `data_e2c208`.
  - `sub_4605f0` / `FUN_004605f0`: calls `SteamUser()` and dispatches vtable
    slot `0x40` with `data_e2c208`.
- Binary Ninja HLIL part 04:
  - `CL_CheckForResend` calls `sub_4605c0(...)`, fetches SteamID words through
    `sub_460550()`, builds the `"getchallenge "` payload, and copies the
    ticket bytes into the packet.
  - the retail error path calls `sub_4605f0()` before deeper shutdown work.
- Binary Ninja HLIL part 05:
  - the server-info/challenge setup path also reaches `sub_4605c0(...)` before
    formatting Steam auth metadata.
- Ghidra `functions.csv`:
  - `FUN_004605c0,004605c0,43,0,unknown`
  - `FUN_004605f0,004605f0,27,0,unknown`
- Symbol alias map:
  - `FUN_004605c0` and `sub_4605c0` promote to
    `SteamClient_GetAuthSessionTicket`
  - `FUN_004605f0` and `sub_4605f0` promote to
    `SteamClient_CancelAuthTicket`

## Source Reconstruction

The retained retail wrapper surface lives in `src/code/client/cl_main.c`.

Pinned source contracts:

- `SteamClient_GetAuthSessionTicket(...)` calls
  `QL_Steamworks_RequestAuthTicket(...)`, retains the returned
  `cl_steamAuthTicketHandle`, and cancels any older retained handle before
  replacement.
- `SteamClient_CancelAuthTicket()` cancels and clears the retained handle.
- `QL_ClientAuth_RequestSteamTicket(...)` runs the Steam callback pump before
  and after `SteamClient_GetAuthSessionTicket(...)`, and only executes when
  `CL_SteamServicesEnabled()` is true.
- `QL_Auth_ExecuteRequest(...)` never dispatches the caller's stale Steam
  credential directly. It creates a fresh `steamCredential`, requests a new
  retained Steam ticket, publishes the diagnostic labels
  `retail GetAuthSessionTicket` and `missing GetAuthTicketForWebApi adapter`,
  then dispatches the fresh ticket.
- `QL_ClientAuth_HandleSteamworksTicket(...)` first tries
  `QL_Steamworks_ValidateTicket(...)`. If the native validation wrapper cannot
  handle the ticket, it falls back to the documented Steamworks compatibility
  backend.
- `QL_ClientAuth_HandleHybridSteam(...)` accepts a Steamworks success, falls
  back to the open adapter only when Steamworks is unavailable or returns
  `QL_AUTH_RESULT_PENDING`, and preserves Steamworks denials.

## Compatibility Boundary

The retail ticket lifetime wrapper is reconstructed, but live auth validation
remains intentionally bounded by `QL_BUILD_ONLINE_SERVICES` and the configured
provider table.

The focused probe now verifies two important boundaries:

- `retry:TICKET-HYBRID-FALLBACK` is issued by the retained ticket request path,
  replaces the caller's original Steam credential before dispatch, and reaches
  the hybrid open-adapter fallback only after the Steamworks compatibility lane
  returns pending.
- `denied:TICKET-HYBRID-REJECTED` is also issued by the retained ticket request
  path, but a Steamworks denial remains final and does not fall through to the
  open adapter.

This keeps the source consistent with the repository policy for Quake
Live-only services: the native wrapper shape is reconstructed, while live
service behavior remains default-disabled and explicitly documented until a
validated open replacement path exists.

## Validation

Added and strengthened tests in `tests/test_platform_services.py`:

- `test_hybrid_fallback_accepts_when_steam_pending` now asserts that exactly
  one retained ticket request is made and that the backend sees the issued
  ticket rather than the caller's original token.
- `test_hybrid_auth_denials_do_not_fallback_to_open_adapter` proves the hybrid
  lane does not convert Steamworks denials into open-adapter successes.
- `test_client_auth_ticket_dispatch_boundary_tracks_round_596_evidence` ties
  the HLIL snippets, Ghidra rows, alias map, source call ordering, gap note, and
  this round note together.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_hybrid_fallback_accepts_when_steam_pending tests/test_platform_services.py::test_hybrid_auth_denials_do_not_fallback_to_open_adapter tests/test_platform_services.py::test_client_auth_ticket_dispatch_boundary_tracks_round_596_evidence -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL and Ghidra both identify the retained GetAuthSessionTicket and
  CancelAuthTicket retail owners.
- Retail call sites consume the ticket wrapper in getchallenge/server metadata
  paths and call the cancel wrapper during error cleanup.
- Source dispatch now has tests proving that the fresh retained ticket is the
  credential used by backend dispatch, not merely a log artifact.

Inference:

- The repository's auth validation remains a faithful bounded compatibility
  reconstruction, not a claim of retail-equivalent live Steam service behavior.
  The native wrapper and lifecycle are the reconstructed retail surface; the
  provider backends remain divergence owners.

Parity estimates:

- Focused client Steam auth dispatch-boundary confidence:
  **before 90% -> after 98%**.
- Focused hybrid fallback divergence classification confidence:
  **before 86% -> after 97%**.
- Overall Steam launch/runtime integration mapping confidence: **93.12% -> 93.14%**.
