# Quake Live Steam Mapping Round 729: Optional Callback Export Fallbacks

Date: 2026-06-16

## Scope

This pass rechecked the Steam callback export boundary that sits between the
retail `SteamAPI_RegisterCallback` / `SteamAPI_RegisterCallResult` imports and
SRP's dynamic, opt-in Steamworks runtime loader. Retail links these exports
directly, but SRP keeps callback and call-result registration optional so a
runtime that lacks those exports can still initialise the retained retail auth
ticket path while disabling callback-dependent adapters.

Focused parity estimate: **before 88% -> after 99%** for focused optional
callback export fallback confidence.
Overall Steam launch/runtime integration mapping confidence moves from **94.28% -> 94.30%**.
Repo-wide parity remains **99%** because this pass strengthens the opt-in
Steamworks harness lane, leaves live service use default-disabled, and does
not change the strict-retail Windows replacement score.
This pass does not change the strict-retail Windows replacement score.

## Evidence

Observed Ghidra corpus facts:

- `imports.txt` retains `STEAM_API.DLL!SteamAPI_RegisterCallback @ 00159248`,
  `STEAM_API.DLL!SteamAPI_UnregisterCallback @ 0015922a`,
  `STEAM_API.DLL!SteamAPI_RegisterCallResult @ 001591ec`, and
  `STEAM_API.DLL!SteamAPI_UnregisterCallResult @ 0015920a`.

Observed Binary Ninja HLIL facts:

- `quakelive_steam.exe_hlil_part19.txt` retains extern rows for the four
  callback and call-result exports.
- `quakelive_steam.exe_hlil_part02.txt` shows the retained callback bootstrap
  calls to `SteamAPI_RegisterCallback`, the UGC call-result handoff through
  `SteamAPI_RegisterCallResult`, and the prior call-result cleanup through
  `SteamAPI_UnregisterCallResult`.

Observed SRP source facts:

- `QL_Steamworks_LoadLibrary` loads the four callback and call-result exports
  through `QL_Steamworks_LoadOptionalSymbol`.
- `QL_Steamworks_RegisterCallbackObject` fails cleanly when
  `SteamAPI_RegisterCallback` is unavailable.
- `QL_Steamworks_UnregisterCallbackObject` clears the local registered flag
  even when the optional `SteamAPI_UnregisterCallback` export is unavailable.
- `QL_Steamworks_HasWebApiAuthTicketAdapter` and
  `QL_Steamworks_RequestWebApiAuthTicket` require the optional Web API ticket
  export, callback registration, and the callback pump before exposing the
  adapter.
- `QL_Steamworks_BindUGCQueryCallResult` fails before binding when
  `SteamAPI_RegisterCallResult` is unavailable, and
  `QL_Steamworks_UnbindCallResultObject` clears local binding state even when
  `SteamAPI_UnregisterCallResult` is unavailable.

Inference: the callback exports are retail-observed but intentionally optional
inside SRP's dynamic runtime boundary. Missing registration exports should keep
Steam init and the retail auth-ticket path usable, while Web API callback
tickets, callback bundles, and UGC call-result binding fail without stale
outputs or fake registrations.

## Source Reconstruction

`tests/steamworks_harness.c` now carries four optional export-availability
switches:

- `steam_api_register_callback_export_available`
- `steam_api_unregister_callback_export_available`
- `steam_api_register_call_result_export_available`
- `steam_api_unregister_call_result_export_available`

The mock `dlsym` path and `QLR_SteamworksMock_PrimeState` both mirror those
switches, so focused tests can exercise either the dynamic loader or direct
source-level state injection without conflating required core runtime exports
with optional callback helpers.

`tests/test_steamworks_harness.py` now proves:

- missing `SteamAPI_RegisterCallback` keeps `QLR_Steamworks_Init` and the
  retail `QLR_Steamworks_Request` auth-ticket path working;
- the same missing registration export disables
  `QLR_Steamworks_HasWebApiAuthTicketAdapter`,
  `QLR_Steamworks_RequestWebApi`, client callback bundles, and server callback
  bundles without registering anything;
- missing `SteamAPI_UnregisterCallback` still clears local callback flags;
- missing `SteamAPI_RegisterCallResult` makes UGC query binding fail cleanly
  and releases the pending UGC query handle;
- missing `SteamAPI_UnregisterCallResult` still clears local UGC call-result
  binding state.

`tests/test_platform_services.py` pins the import/HLIL evidence, the optional
production loader shape, the harness export toggles, the focused ctypes
regressions, and this mapping round.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "missing_optional_callback or missing_optional_call_result or missing_web_api_ticket_export" --tb=short`
  - `10 passed, 174 deselected in 2.42s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_mock_loader_export_constants_round_715" --tb=short`
  - `1 passed, 265 deselected in 9.87s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks_optional_callback_export_fallbacks_round_729 or steamworks_mock_loader_export_constants_round_715 or steamworks_web_api_optional_export_round_719" --tb=short`
  - `3 passed, 265 deselected in 0.13s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `184 passed in 1.18s`
- `python -m pytest -q tests/test_platform_services.py -k "steamworks" --tb=short`
  - `18 passed, 250 deselected in 11.53s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `267 passed, 1 failed in 13.81s`; the failure is the unrelated ZMQ
    Round 649 static gate expecting the older direct `zmq_bind` condition
    text in `idZMQ_EnsureRconSocket`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.

Round 731 later pinned the optional auxiliary client interface export
fallbacks for `SteamUtils`, `SteamUserStats`, `SteamNetworking`, and
`SteamMatchmakingServers`.
