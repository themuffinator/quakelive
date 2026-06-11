# Quake Live Steam Mapping Round 538: Server Lifecycle Helper Alias Bridge

## Scope

This pass tightens the server-side Steam launch/runtime helper band in retail
`quakelive_steam.exe`. The focus is the GameServer lifecycle, identity,
packet, heartbeat, unauthenticated-user, and auth-session helpers surrounding
the already reconstructed server callback and bootstrap paths.

| Retail address | Ghidra name | Binary Ninja name | Promoted name | Confidence |
| --- | --- | --- | --- | --- |
| `0x00465a30` | `FUN_00465a30` | `sub_465a30` | `SteamServer_IsInitialized` | High |
| `0x00465a60` | `FUN_00465a60` | `sub_465a60` | `SteamServer_SetKeyValuesFromInfoString` | High |
| `0x00465b00` | `FUN_00465b00` | `sub_465b00` | `SteamServer_PublishSteamID` | High |
| `0x00465d30` | `FUN_00465d30` | `sub_465d30` | `SteamServer_Shutdown` | High |
| `0x00465d50` | `FUN_00465d50` | `sub_465d50` | `SteamServer_HandleIncomingPacket` | High |
| `0x00465db0` | `FUN_00465db0` | `sub_465db0` | `SteamServer_EnableHeartbeats` | High |
| `0x00465df0` | `FUN_00465df0` | `sub_465df0` | `SteamServer_CreateUnauthenticatedUserConnection` | High |
| `0x00465e30` | `FUN_00465e30` | `sub_465e30` | `SteamServer_InitDefaultHostname` | High |
| `0x00465e80` | `FUN_00465e80` | `sub_465e80` | `SteamServer_GetPublicIP` | High |
| `0x00465fd0` | `FUN_00465fd0` | `sub_465fd0` | `SteamServer_BeginAuthSession` | High |
| `0x004661e0` | `FUN_004661e0` | `sub_4661e0` | `SteamServer_EndAuthSession` | High |
| `0x00466b90` | `FUN_00466b90` | `sub_466b90` | `SteamServer_EndOrphanedAuthSessions` | High |
| `0x00466ed0` | `FUN_00466ed0` | `sub_466ed0` | `SteamServer_Init` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  emits concrete rows for every promoted helper in this pass, including byte
  sizes from the 6-byte initialized guard at `0x00465a30` through the 535-byte
  orphaned-auth-session sweep at `0x00466b90`.
- Binary Ninja HLIL names the same retail addresses as the corresponding
  `sub_*` functions and shows the Steam GameServer interface calls:
  - `sub_465d30` calls `SteamGameServer_Shutdown` and clears the initialized
    flag after the call.
  - `sub_465d50` routes incoming UDP payloads through the GameServer
    `HandleIncomingPacket` slot.
  - `sub_465db0` toggles the `EnableHeartbeats` slot at vtable offset `0x9c`.
  - `sub_465df0` calls the unauthenticated-user connection slot at `0x64`.
  - `sub_465fd0` and `sub_4661e0` own `BeginAuthSession` and
    `EndAuthSession` flow respectively.
  - `sub_466b90` scans authenticated clients and ends orphaned Steam auth
    sessions only when the GameServer interface is initialized.
- Ghidra `imports.txt` confirms the owning import surface for this band:
  `SteamGameServer`, `SteamGameServerNetworking`,
  `SteamGameServer_Init`, `SteamGameServer_Shutdown`,
  `SteamGameServer_RunCallbacks`, `SteamGameServerStats`,
  `SteamGameServerUGC`, and `SteamGameServerUtils`.

Inferred meaning:

- The reconstructed source already mirrors the retail ownership split: common
  bootstrap initializes GameServer, server code publishes identity/state and
  handles auth-session lifetimes, and the platform layer owns direct vtable
  calls. This round makes the alias corpus reflect that split across both
  Ghidra and Binary Ninja names.
- The lower-case `sub_*` spellings are retained because the committed HLIL
  uses them, while the existing upper-case aliases remain for older tests and
  notes.

## Reconstruction

- Promoted Ghidra-style aliases for the server lifecycle/auth helper band:
  `FUN_00465a30`, `FUN_00465a60`, `FUN_00465b00`, `FUN_00465d30`,
  `FUN_00465d50`, `FUN_00465db0`, `FUN_00465df0`, `FUN_00465e30`,
  `FUN_00465e80`, `FUN_00465fd0`, `FUN_004661e0`, and `FUN_00466b90`.
- Added lower-case Binary Ninja spellings for the same helpers, plus
  `sub_466ed0` for the already promoted `SteamServer_Init` constructor.
- Strengthened
  `test_server_game_server_wrappers_reconstruct_mapped_server_slots` so it
  now cross-checks:
  - the full promoted alias set from
    `references/analysis/quakelive_symbol_aliases.json`;
  - the Ghidra `functions.csv` row and byte-size anchors for each helper;
  - existing HLIL anchors for Steam GameServer shutdown, init, packet,
    heartbeat, unauthenticated-user, and auth-session behavior;
  - the existing reconstructed source wrappers in
    `src/common/platform/platform_steamworks.c`.

## Remaining Boundary

This pass is name/evidence reconstruction only. Steam GameServer behavior
remains controlled by the existing platform-service and online-services
gates, with live-service use still disabled by default.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json`
- `python -m pytest tests\test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
- `python -m pytest tests\test_platform_services.py -q --tb=short`
- `python -m pytest tests\test_steamworks_harness.py -q --tb=short`

No runtime launch was performed; committed retail HLIL, Ghidra metadata, and
source parity tests were sufficient.

## Parity Estimate

- Focused Steam server lifecycle/auth helper alias bridge:
  **before 72% -> after 99%**
- Focused Ghidra/Binary Ninja helper-band evidence coverage:
  **before 90% -> after 98%**
- Overall Steam launch/runtime reconstruction parity:
  **before 91.95% -> after 92.0%**
