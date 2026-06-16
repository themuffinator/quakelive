# Quake Live Steam Mapping Round 716: Web API Ticket Callback Failure Wiring

Date: 2026-06-16

## Scope

This pass rechecked the client Steam callback pump and the optional SRP
`GetAuthTicketForWebApi` adapter that sits behind the documented
`QL_BUILD_ONLINE_SERVICES` Steamworks lane. Retail Quake Live uses
`SteamAPI_RegisterCallback` and `SteamAPI_RunCallbacks` for retained callback
objects; SRP uses the same callback object machinery for the newer Web API auth
ticket adapter when the loaded Steam runtime exposes it.

Focused parity estimate: **before 88% -> after 99%** for focused Web API
ticket callback failure-path confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.14% -> 94.16%**. Repo-wide parity remains **99%** because this pass strengthens the opt-in Steamworks harness lane, leaves default online services disabled, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra import-table facts:

- `imports.txt` retains `STEAM_API.DLL!SteamAPI_RegisterCallback @ 00159248`.
- `imports.txt` retains `STEAM_API.DLL!SteamAPI_RunCallbacks @ 00159274`.

Observed Binary Ninja HLIL facts:

- `004613f5` registers a client callback object with callback id `0x151`.
- `00461d63` pumps client callbacks with `SteamAPI_RunCallbacks()`.

Observed SRP adapter facts:

- `QL_STEAM_CALLBACK_GET_TICKET_FOR_WEB_API_RESPONSE` is `0xa8`, the Steam
  callback id used by `GetTicketForWebApiResponse_t`.
- `QL_Steamworks_RegisterWebApiAuthTicketCallback` prepares the same retained
  callback object shape as the retail callback bundle and binds
  `QL_Steamworks_DispatchGetTicketForWebApiResponse`.
- `QL_Steamworks_RequestWebApiAuthTicket` pumps
  `QL_STEAM_WEB_API_TICKET_CALLBACK_PUMPS` iterations, cancels the returned
  handle on timeout, cancels on non-OK Steam result, cancels on empty or
  oversized callback ticket data, and cancels if hex encoding cannot fit.

Inference: the executable Steamworks harness needs independent control over the
returned ticket handle, callback handle, callback length, callback queueing, and
Steam result. Without those controls, tests can prove only the happy path and
cannot distinguish timeout, mismatched-handle, rejected-result, or malformed
payload behavior.

## Source Reconstruction

`tests/steamworks_harness.c` now mirrors the Web API callback result more
closely:

- `QLR_STEAM_CALLBACK_GET_TICKET_FOR_WEB_API_RESPONSE` remains pinned to
  `0xa8`.
- `QLR_STEAM_ERESULT_OK` names the success value used by the mock response.
- The mock state tracks `web_api_ticket_callback_handle`,
  `web_api_ticket_callback_length`, and `web_api_ticket_queue_callback`
  separately from the returned `web_api_ticket_handle`.
- `QLR_SteamworksMock_SetWebApiTicketCallbackBehavior` can suppress callback
  queueing, queue a mismatched handle, or report a callback length that differs
  from the stored mock ticket bytes.
- `QLR_SteamAPI_GetAuthTicketForWebApi` now builds the raw callback event with
  bounded copying, so oversized reported lengths exercise production rejection
  logic without overflowing the mock payload buffer.

`tests/test_steamworks_harness.py` now includes
`test_web_api_auth_ticket_adapter_cancels_unusable_callback_results`, covering:

- missing callback delivery, which times out and cancels the returned ticket;
- mismatched callback handle, which is ignored by
  `QL_Steamworks_DispatchGetTicketForWebApiResponse` and then cancelled;
- non-OK Steam result, which is surfaced through `steamResult` and cancelled;
- oversized callback ticket length, which completes the callback but leaves no
  usable ticket payload and cancels.

`tests/test_platform_services.py` pins the source shape for the production
callback registration, dispatch guards, cancellation branches, mock callback
controls, and this mapping round.

Round 717 later pinned the Web API callback lifecycle handoff: a registered
Web API ticket callback is unregistered before the normal client callback
bundle is rebuilt, preventing stale callback registrations.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "web_api_auth_ticket_adapter" --tb=short`
  - `10 passed, 134 deselected in 1.94s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_web_api_callback_failure_round_716 or steamworks_mock_loader_export_constants_round_715" --tb=short`
  - `2 passed, 253 deselected in 0.12s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `144 passed in 0.94s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `254 passed, 1 failed in 10.33s`; the failure is the pre-existing Round
    698 gate referencing missing
    `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
