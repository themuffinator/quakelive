# Quake Live Steam Mapping Round 718: Web API Callback Reuse

Date: 2026-06-16

## Scope

This pass rechecked sequential Web API auth-ticket requests on top of the
retained Steam callback object machinery. Rounds 716 and 717 pinned failure
handling and lifecycle handoff; this round pins reuse of the already-registered
`GetTicketForWebApiResponse_t` callback across multiple successful ticket
requests.

Focused parity estimate: **before 87% -> after 99%** for focused Web API
callback sequential-reuse confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.18% -> 94.20%**. Repo-wide parity remains
**99%** because this pass strengthens the opt-in Steamworks harness lane,
leaves production behavior unchanged, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra import-table fact:

- `imports.txt` retains `STEAM_API.DLL!SteamAPI_RegisterCallback @ 00159248`.

Observed Binary Ninja HLIL facts:

- `004613f5` registers the retained rich-presence callback `0x151`.
- `004614ed` registers the retained friend-rich-presence callback `0x150`.

Observed SRP source facts:

- `QL_Steamworks_RegisterWebApiAuthTicketCallback` checks
  `callbackState->webApiTicketResponse.callbackFlags & QL_STEAM_CALLBACK_FLAG_REGISTERED`
  and returns `qtrue` before preparing or registering a replacement callback.
- `QL_Steamworks_RequestWebApiAuthTicket` registers the Web API callback before
  calling `QL_Steamworks_ResetWebApiAuthTicketState`.
- `QL_Steamworks_ResetWebApiAuthTicketState` clears only the active request
  fields and callback payload buffer. It does not clear or rebuild
  `webApiTicketResponse`.

Inference: sequential Web API ticket requests should reuse one retained callback
object while each request still resets active state, accepts a fresh ticket
handle, and captures fresh callback payload bytes.

## Source Reconstruction

`tests/test_steamworks_harness.py` now includes
`test_web_api_ticket_callback_is_reused_across_sequential_requests`, which
proves:

- the first Web API ticket request registers one callback and returns handle
  `41` with the default `abcdef` hex payload;
- the second request changes the mock ticket bytes and handle to `42`, returns
  `01234567`, and does not issue another `SteamAPI_RegisterCallback`;
- `QLR_SteamworksMock_GetRegisteredCallbackCount` remains `1` across both
  successful requests;
- `QLR_SteamworksMock_GetWebApiTicketCallbackRegistered` remains true across
  both successful requests;
- no cancellation is emitted for either successful request;
- final harness unregister removes the one retained Web API callback.

`tests/test_platform_services.py` pins the retail registration evidence,
production early-return source shape, reset-state boundary, focused ctypes
regression, and this mapping round.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "web_api_ticket_callback_is_reused_across_sequential_requests or web_api_ticket_callback_yields_to_client_callback_bundle or web_api_auth_ticket_adapter" --tb=short`
  - `14 passed, 134 deselected in 1.98s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_web_api_callback_reuse_round_718 or steamworks_web_api_callback_lifecycle_round_717" --tb=short`
  - `2 passed, 255 deselected in 4.19s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `148 passed in 0.88s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `256 passed, 1 failed in 10.14s`; the failure is the pre-existing Round
    698 gate referencing missing
    `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.

Round 719 later pinned the optional Web API auth-ticket export boundary,
proving the retail GetAuthSessionTicket path remains usable when
GetAuthTicketForWebApi is absent.
