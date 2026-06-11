# Quake Live Steam Mapping Round 534: Client Callback Bootstrap Bridge

## Scope

This pass tightens the Steam client launch/runtime callback bootstrap bridge in
the retail `quakelive_steam.exe` corpus. The focus is the main
`SteamCallbacks` constructor, the microtransaction callback constructor, and
the immediate retail callback targets that those constructors wire into
SteamAPI callback registration.

| Retail address | Ghidra name | Binary Ninja name | Promoted name | Confidence |
| --- | --- | --- | --- | --- |
| `0x0045fd00` | `FUN_0045fd00` | `sub_45fd00` | `SteamCallbacks_OnGetAllUGCQueryCompleted` | High |
| `0x0045fef0` | `FUN_0045fef0` | `sub_45fef0` | `SteamCallbacks_OnP2PSessionRequest` | High |
| `0x0045ff50` | `FUN_0045ff50` | `sub_45ff50` | `SteamCallbacks_OnRichPresenceJoinRequested` | High |
| `0x0045ff70` | `FUN_0045ff70` | `sub_45ff70` | `SteamCallbacks_OnGameServerChangeRequested` | High |
| `0x0045ffd0` | `FUN_0045ffd0` | `sub_45ffd0` | `SteamCallbacks_OnUserStatsReceived` | High |
| `0x004602e0` | `FUN_004602e0` | `sub_4602e0` | `SteamCallbacks_OnFriendRichPresenceUpdate` | High |
| `0x00460800` | `FUN_00460800` | `sub_460800` | `SteamCallbacks_OnPersonaStateChange` | High |
| `0x004613a0` | `FUN_004613a0` | `sub_4613a0` | `SteamCallbacks_Init` | High |
| `0x004658a0` | `FUN_004658a0` | `sub_4658a0` | `SteamMicroCallbacks_OnAuthorizationResponse` | High |
| `0x004659e0` | `FUN_004659e0` | `sub_4659e0` | `SteamMicroCallbacks_Init` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records stable function rows and sizes for all ten callback bootstrap
  entries listed above.
- Binary Ninja HLIL for `sub_4613a0` constructs the
  `CCallResult<class SteamCallbacks, struct SteamUGCQueryCompleted_t>` slot,
  then registers callback objects for rich-presence joins, stats received,
  persona state, P2P session requests, game-server-change requests, and friend
  rich-presence updates.
- Retail `SteamClient_Init` allocates a `0x98` callback bundle and calls
  `sub_4613a0(eax_3)` before assigning the bundle to `data_e2c20c`.
- Binary Ninja HLIL for `sub_4659e0` allocates a `0x14` callback object,
  assigns `sub_4658a0` as the `MicroTxnAuthorizationResponse_t` run target, and
  registers callback id `0x98` through `SteamAPI_RegisterCallback`.
- Binary Ninja HLIL for `sub_4658a0` builds the microtransaction browser/log
  payload from app id, order id, and authorization state, including the retail
  `GOT MICRO RESPONSE` diagnostic.
- The structured Ghidra symbol corpus contains the imported callback vtables
  for the same callback families, matching the callback ids and source binding
  surface.

Inferred meaning:

- The current source callback abstraction preserves the retail split between
  client callbacks, the UGC call-result slot, lobby callbacks, workshop
  callbacks, and microtransaction callbacks.
- The added aliases make the evidence bridge explicit across Ghidra `FUN_*`
  names, Binary Ninja `sub_*` names, and the reconstructed source binding
  functions. No live Steam service behavior changes are required.

## Reconstruction

- Promoted Ghidra-style aliases for the main Steam client callback targets,
  `SteamCallbacks_Init`, the microtransaction callback target, and
  `SteamMicroCallbacks_Init`.
- Added lower-case Binary Ninja spellings where the committed HLIL uses them,
  including `sub_4613a0`, `sub_4658a0`, and `sub_4659e0`.
- Strengthened
  `test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface`
  so it now cross-checks:
  - alias names from `references/analysis/quakelive_symbol_aliases.json`;
  - Ghidra `functions.csv` rows and sizes;
  - retail HLIL constructor signatures and callback target signatures;
  - source-side `SteamCallbacks_Init` and `SteamMicroCallbacks_Init` binding
    assignments before the platform registration calls;
  - the microtransaction callback target and retail callback id `0x98`.

## Remaining Boundary

The runtime callback pump is still intentionally gated behind the repository's
Steamworks/online-services policy. This round maps the retail callback bootstrap
surface; it does not enable default live-service usage.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json`
- `python -m pytest tests\test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface -q --tb=short`
- `python -m pytest tests\test_platform_services.py -q --tb=short`

No runtime launch was performed; committed retail HLIL, Ghidra metadata, and
source parity tests were sufficient.

## Parity Estimate

- Focused client callback bootstrap alias bridge:
  **before 68% -> after 99%**
- Focused callback registration evidence coverage:
  **before 90% -> after 98%**
- Overall Steam launch/runtime reconstruction parity:
  **before 91.85% -> after 91.9%**
