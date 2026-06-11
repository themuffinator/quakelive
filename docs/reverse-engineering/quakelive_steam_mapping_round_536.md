# Quake Live Steam Mapping Round 536: GameServer Callback Bootstrap Bridge

## Scope

This pass tightens the server-side Steam launch/runtime callback bridge in the
retail `quakelive_steam.exe` corpus. The focus is the
`SteamServerCallbacks_Init` constructor and the immediate GameServer callback
targets for connection state, auth-ticket validation, and server-side P2P
session requests.

| Retail address | Ghidra name | Binary Ninja name | Promoted name | Confidence |
| --- | --- | --- | --- | --- |
| `0x00465b70` | `FUN_00465b70` | `sub_465b70` | `SteamServerCallbacks_OnP2PSessionRequest` | High |
| `0x00465c10` | not emitted as `FUN_*` row | `sub_465c10` | `SteamServerCallbacks_OnConnectFailure` | High |
| `0x00465c30` | not emitted as `FUN_*` row | `sub_465c30` | `SteamServerCallbacks_OnServersDisconnected` | High |
| `0x00465c50` | `FUN_00465c50` | `sub_465c50` | `SteamServerCallbacks_OnValidateAuthTicketResponse` | High |
| `0x00466800` | not emitted as `FUN_*` row | `sub_466800` | `SteamServerCallbacks_OnServersConnected` | High |
| `0x00466db0` | `FUN_00466db0` | `sub_466db0` | `SteamServerCallbacks_Init` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00465b70` as 146 bytes, `FUN_00465c50` as 209 bytes, and
  `FUN_00466db0` as 272 bytes.
- Binary Ninja HLIL identifies the smaller connected, failure, and disconnect
  callback targets as `sub_466800`, `sub_465c10`, and `sub_465c30` even though
  those addresses are not emitted as separate Ghidra `FUN_*` rows in the
  committed `functions.csv`.
- Retail `sub_466db0` constructs the GameServer callback bundle and sets
  callback flag `2` on each callback object, matching Steam's GameServer-side
  callback registration.
- Retail `sub_466db0` registers:
  - `SteamServersConnected_t` id `0x65` with `sub_466800`;
  - `SteamServerConnectFailure_t` id `0x66` with `sub_465c10`;
  - `SteamServersDisconnected_t` id `0x67` with `sub_465c30`;
  - `ValidateAuthTicketResponse_t` id `0x8f` with `sub_465c50`;
  - server-side `P2PSessionRequest_t` id `0x4b2` with `sub_465b70`.
- Retail `sub_466800` logs `Connected to Steam servers`, marks
  `data_e30354 = 1`, publishes the server SteamID, pushes published server
  state, requests stats, and publishes key/value server info.
- Retail `sub_465b70` accepts P2P sessions only when the incoming SteamID
  matches an active server client slot; otherwise it logs the refused request.

Inferred meaning:

- The reconstructed source already preserves the retail owner split:
  `SV_SteamServerInitCallbacks` binds server handlers, while
  `QL_Steamworks_RegisterServerCallbacks` owns the Steam callback objects and
  marks them as GameServer callbacks.
- The alias bridge should therefore promote only the Ghidra `FUN_*` names that
  are present in the committed Ghidra inventory and separately preserve the
  Binary Ninja-only `sub_*` names for the smaller callback targets.

## Reconstruction

- Promoted Ghidra-style aliases for:
  - `FUN_00465b70 -> SteamServerCallbacks_OnP2PSessionRequest`
  - `FUN_00465c50 -> SteamServerCallbacks_OnValidateAuthTicketResponse`
  - `FUN_00466db0 -> SteamServerCallbacks_Init`
- Added lower-case Binary Ninja spellings for the GameServer callback targets
  and constructor, including `sub_465b70`, `sub_465c10`, `sub_465c30`,
  `sub_465c50`, and `sub_466db0`.
- Strengthened
  `test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle`
  so it now cross-checks:
  - alias names from `references/analysis/quakelive_symbol_aliases.json`;
  - Ghidra `functions.csv` rows where present;
  - source binding assignments in `SV_SteamServerInitCallbacks`;
  - existing retail HLIL anchors for connection, auth, P2P, and callback
    constructor behavior.

## Remaining Boundary

The source keeps GameServer callback registration behind the existing
Steamworks/online-services policy and platform-service gates. This round maps
the retail callback bootstrap surface; it does not enable default live-service
usage.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json`
- `python -m pytest tests\test_platform_services.py::test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle -q --tb=short`
- `python -m pytest tests\test_platform_services.py -q --tb=short`
- `python -m pytest tests\test_steamworks_harness.py -q --tb=short`

No runtime launch was performed; committed retail HLIL, Ghidra metadata, and
source parity tests were sufficient.

## Parity Estimate

- Focused GameServer callback bootstrap alias bridge:
  **before 70% -> after 99%**
- Focused server callback registration evidence coverage:
  **before 92% -> after 98%**
- Overall Steam launch/runtime reconstruction parity:
  **before 91.9% -> after 91.95%**
