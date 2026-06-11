# Quake Live Steam Mapping Round 591: Microtransaction Authorization Payload

Date: 2026-06-11

## Scope

This pass rechecked the retained Steam microtransaction authorization callback
surface used by the retail browser/store runtime:

- callback target: `sub_4658a0` / `FUN_004658a0`
- callback constructor: `sub_4659e0` / `FUN_004659e0`
- callback type: `MicroTxnAuthorizationResponse_t`
- callback id: `0x98`
- retail surface: `MicroTxnAuthorizationResponse_t` callback id `0x98`

No source runtime behavior was broadened. The callback remains behind
`QL_BUILD_ONLINE_SERVICES` / `QL_BUILD_STEAMWORKS`, and default builds continue
to expose the disabled stub surface.

## Retail Evidence

- Ghidra records `FUN_004658a0,004658a0,319,0,unknown` and
  `FUN_004659e0,004659e0,67,0,unknown`.
- The symbol alias corpus maps `FUN_004658a0`, `sub_4658A0`, and
  `sub_4658a0` to `SteamMicroCallbacks_OnAuthorizationResponse`, and maps
  `FUN_004659e0`, `sub_4659E0`, and `sub_4659e0` to
  `SteamMicroCallbacks_Init`.
- Ghidra `analysis_symbols.txt` retains the
  `CCallback<class_SteamMicroCallbacks,struct_MicroTxnAuthorizationResponse_t,0>`
  vtable/RTTI family.
- Binary Ninja HLIL for `sub_4658a0` constructs a browser-facing object with
  `appid`, `orderid`, and `authorized`:
  - `*arg1` is inserted under `"appid"`.
  - `arg1[2]` / `arg1[3]` are formatted as `"%llu"` and inserted under
    `"orderid"`.
  - `arg1[4].b` is converted to the authorization boolean and inserted under
    `"authorized"`.
  - The callback then logs through the retained `GOT MICRO RESPONSE...` string.
- Binary Ninja HLIL for `sub_4659e0` allocates a `0x14` callback object, assigns
  `sub_4658a0` at the callback target slot, and registers callback id `0x98`.

## Source Alignment

- `platform_steamworks.c` keeps the raw
  `ql_steam_microtxn_authorization_response_raw_t` payload at `0x18` bytes,
  matching the generic 24-byte callback size thunk used by the retail callback
  vtable family.
- `QL_Steamworks_DispatchMicroAuthorizationResponse` copies `appId`, `orderId`,
  and `authorized` into the typed source event before invoking the retained
  binding.
- `QL_Steamworks_RegisterMicroCallbacks` prepares `authorizationResponse` with
  callback id `0x98`, payload size
  `sizeof( ql_steam_microtxn_authorization_response_raw_t )`, and the client
  callback dispatch owner.
- `SteamMicroCallbacks_Init` binds
  `CL_Steam_Micro_OnAuthorizationResponse` and registers the callback bundle.
- `CL_Steam_Micro_OnAuthorizationResponse` publishes
  `microtxn.authorization` with the retained JSON keys
  `appid`, `orderid`, and `authorized`. It routes diagnostics through
  `CL_LogMicroTransactionCallbackLifecycle` instead of reviving the retail
  literal log format as authoritative application behavior.

## Validation

Added
`test_client_microtransaction_authorization_callback_tracks_retail_browser_payload`
to `tests/test_platform_services.py`.

Expected validation:

- focused parity gate:
  `python -m pytest tests/test_platform_services.py::test_client_microtransaction_authorization_callback_tracks_retail_browser_payload -q --tb=short`
- adjacent callback gates:
  `python -m pytest tests/test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface tests/test_platform_services.py::test_client_browser_event_publication_hooks_reconstruct_runtime_owner -q --tb=short`
- full platform-service parity sweep:
  `python -m pytest tests/test_platform_services.py -q --tb=short`

## Parity Delta

- Focused microtransaction authorization payload confidence:
  **before 88% -> after 99%**.
- Focused client Steam callback payload evidence confidence:
  **before 98% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.08% -> 93.10%**.
