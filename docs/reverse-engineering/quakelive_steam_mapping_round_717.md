# Quake Live Steam Mapping Round 717: Web API Callback Lifecycle Handoff

Date: 2026-06-16

## Scope

This pass rechecked the client callback lifecycle around SRP's optional
`GetAuthTicketForWebApi` adapter. Round 716 pinned callback failure behavior;
this round pins what happens after that callback has been registered and the
normal retained Steam client callback bundle is initialized.

Focused parity estimate: **before 86% -> after 99%** for focused Web API
callback lifecycle-handoff confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.16% -> 94.18%**. Repo-wide parity remains
**99%** because this pass strengthens the opt-in Steamworks harness lane,
leaves production behavior unchanged, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra import-table facts:

- `imports.txt` retains `STEAM_API.DLL!SteamAPI_RegisterCallback @ 00159248`.
- `imports.txt` retains `STEAM_API.DLL!SteamAPI_UnregisterCallback @ 0015922a`.

Observed Binary Ninja HLIL facts:

- `004613f5` registers the retained rich-presence callback `0x151`.
- `004614ed` registers the retained friend-rich-presence callback `0x150`.
- `0046743d` and `004675b0` show callback unregister edges through
  `SteamAPI_UnregisterCallback`.

Observed SRP source facts:

- `QL_Steamworks_RegisterWebApiAuthTicketCallback` registers
  `webApiTicketResponse` on demand for `GetTicketForWebApiResponse_t`.
- `QL_Steamworks_RegisterClientCallbacks` checks both `registered` and
  `webApiTicketResponse.callbackFlags & QL_STEAM_CALLBACK_FLAG_REGISTERED`.
  If either is set, it calls `QL_Steamworks_UnregisterClientCallbacks()` before
  rebuilding the normal client callback bundle.
- `QL_Steamworks_UnregisterClientCallbacks` explicitly unregisters
  `QL_Steamworks_UnregisterCallbackObject( &callbackState->webApiTicketResponse )`
  before unregistering the normal client callbacks, then clears the retained
  state.

Inference: the Web API auth-ticket adapter must not leave a stale callback
object that blocks or aliases the normal client callback bundle. The executable
harness needs visibility into that handoff so the behavior is pinned beyond
static source assertions.

## Source Reconstruction

`tests/steamworks_harness.c` now exposes read-only probes for the retained
callback lifecycle:

- `QLR_SteamworksMock_GetWebApiTicketCallbackRegistered` reports the
  `webApiTicketResponse` registration flag.
- `QLR_SteamworksMock_GetRegisteredCallbackCount` reports the mock Steam
  registration table count.

`tests/test_steamworks_harness.py` now includes
`test_web_api_ticket_callback_yields_to_client_callback_bundle`, which proves:

- a successful Web API ticket request registers exactly one Web API callback;
- the normal client callback bundle unregisters that Web API callback before
  installing the harness callback bundle;
- the registration count becomes the full 18-callback harness bundle rather
  than 19 stale callbacks;
- rich-presence dispatch still works through the normal client callback pump;
- final harness unregister tears the mock registration table back down to zero.

`tests/test_platform_services.py` pins the retail import/HLIL evidence,
production handoff source shape, harness probes, focused ctypes regression,
and this mapping round.

Round 718 later pinned sequential Web API auth-ticket callback reuse so
multiple successful ticket requests share the already-registered
`webApiTicketResponse` callback object while returning fresh handles and
payloads.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "web_api_ticket_callback_yields_to_client_callback_bundle or web_api_auth_ticket_adapter" --tb=short`
  - `12 passed, 134 deselected in 1.96s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_web_api_callback_lifecycle_round_717 or steamworks_web_api_callback_failure_round_716" --tb=short`
  - `2 passed, 254 deselected in 4.09s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `146 passed in 0.99s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `255 passed, 1 failed in 9.91s`; the failure is the pre-existing Round
    698 gate referencing missing
    `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
