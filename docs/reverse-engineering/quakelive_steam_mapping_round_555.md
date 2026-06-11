# Quake Live Steam Mapping Round 555: Callback Base Vtable and Raw Payload ABI

Date: 2026-06-11

## Scope

This round rechecked the shared Steam `CCallbackBase` vtable helpers and the
raw callback payload byte counts used by retail `quakelive_steam.exe`.

The goal was to finish the callback-size map started in the previous Steam
round, promote the remaining common callback helper aliases, and correct raw
source payload layouts where host compiler alignment or newer SDK fields had
drifted from the retail Quake Live ABI. No live Steam services were enabled.

Evidence used:

- Ghidra `functions.csv` rows for `0x00461050..0x00461090`,
  `0x00463600`, `0x00467450`, `0x00467480`, and `0x00469310`
- Binary Ninja HLIL part 02 for callback run helpers and constant
  payload-size thunks
- Binary Ninja HLIL part 06 for callback vtable consumers across client,
  avatar, lobby, microtransaction, server, stats, and workshop owners
- reconstructed source anchors in `platform_steamworks.c`,
  `tests/steamworks_harness.c`, and the platform-services parity tests

## Observed Facts

| Raw symbol | Alias | Observed signal | Reconstruction status |
| --- | --- | --- | --- |
| `sub_469310` | `SteamCallback_Run` | Common `vFunc_0`; HLIL calls the retained callback target at `this + 0x10` with the payload argument. | Source-backed by `QL_Steamworks_CallbackRun`. |
| `sub_461050` | `SteamCallback_RunCallResult` | Common `vFunc_1`; HLIL tail-dispatches to the retained callback target. | Source-backed by `QL_Steamworks_CallbackRunCallResult`. |
| `sub_461060` | `SteamCallback_GetPayloadSize264` | Returns `0x108`; used by `GameRichPresenceJoinRequested_t`. | Source raw size is pinned at `0x108`. |
| `sub_461070` | `SteamCallback_GetPayloadSize16` | Returns `0x10`; used by persona/lobby-created/game-lobby-join/workshop-installed style payloads. | Source raw sizes are pinned at `0x10` where applicable. |
| `sub_461080` | `SteamCallback_GetPayloadSize8` | Returns `8`; used by client and server `P2PSessionRequest_t`. | Source raw size is pinned at `0x08`. |
| `sub_461090` | `SteamCallback_GetPayloadSize128` | Returns `0x80`; used by `GameServerChangeRequested_t`. | Source raw size is pinned at `0x80`. |
| `sub_463600` | `SteamCallback_GetPayloadSize20` | Returns `0x14`; used by `AvatarImageLoaded_t` and `ValidateAuthTicketResponse_t`. | Source raw payloads now use explicit 32-bit SteamID words to stay 20 bytes on all hosts. |
| `sub_467450` | `SteamCallback_GetPayloadSize1` | Returns `1`; used by server-connected callbacks. | Source raw size is pinned at `0x01`. |
| `sub_467480` | `SteamCallback_GetPayloadSize12` | Returns `0x0c`; used by friend-rich-presence and GS stats callbacks. | Source raw payloads now use explicit 32-bit SteamID words to stay 12 bytes on all hosts. |

## Source Reconstruction

The source callback object still intentionally uses one retained vtable with a
dynamic `payloadSize` field. This is equivalent to the retail constant thunk
family as long as each registered raw payload byte count matches retail.

This round corrected the raw source ABI for callbacks whose retail payloads are
smaller than the natural 64-bit host layout:

- `ql_steam_friend_rich_presence_update_raw_t` now stores the SteamID as
  low/high 32-bit words and remains `0x0c` bytes.
- `ql_steam_avatar_image_loaded_raw_t` now stores the SteamID as low/high
  32-bit words and remains `0x14` bytes.
- `ql_steam_validate_auth_ticket_response_raw_t` now stores both SteamIDs as
  low/high 32-bit words and remains `0x14` bytes.
- `ql_steam_gs_stats_received_raw_t` and
  `ql_steam_gs_stats_stored_raw_t` now store the SteamID as low/high words and
  remain `0x0c` bytes.
- `ql_steam_download_item_result_raw_t` now carries an explicit trailing
  padding word so the source registration matches retail's `0x18` bytes.
- `ql_steam_ugc_query_completed_raw_t` dropped the newer SDK
  `nextCursor[256]` tail; retail's call-result vtable reports `0x18` bytes and
  the reconstructed dispatch path does not consume a cursor.

Compile-time size guards now pin the retail byte counts for the callback raw
payload structs covered by the mapped thunk family.

## Alias Promotion

Promoted spelling groups:

- `FUN_00461050`, `sub_461050` -> `SteamCallback_RunCallResult`
- `FUN_00461060`, `sub_461060` -> `SteamCallback_GetPayloadSize264`
- `FUN_00461070`, `sub_461070` -> `SteamCallback_GetPayloadSize16`
- `FUN_00461080`, `sub_461080` -> `SteamCallback_GetPayloadSize8`
- `FUN_00461090`, `sub_461090` -> `SteamCallback_GetPayloadSize128`
- `FUN_00463600`, `sub_463600` -> `SteamCallback_GetPayloadSize20`
- `FUN_00467450`, `sub_467450` -> `SteamCallback_GetPayloadSize1`
- `FUN_00467480`, `sub_467480` -> `SteamCallback_GetPayloadSize12`
- `FUN_00469310`, `sub_469310` -> `SteamCallback_Run`

## Inference Boundary

Observed facts:

1. Retail callback vtables consistently use `sub_469310` for normal callback
   dispatch and `sub_461050` for the second callback run slot.
2. Every callback payload size covered here is a pure constant-return body.
3. Part 06 vtable consumers tie each size thunk to concrete callback template
   instantiations.
4. Retail `SteamUGCQueryCompleted_t` uses the same `0x18` size thunk as the
   other 24-byte callbacks.

Inference:

1. The dynamic source `payloadSize` field is faithful to retail when backed by
   compile-time raw-size guards, even though retail emits one constant function
   per payload-size bucket.

## Parity Estimate

- Focused callback-base vtable helper alias confidence:
  **45% -> 99%**
- Focused raw callback payload ABI parity:
  **86% -> 99%**
- Focused Steam callback registration/source layout confidence:
  **94% -> 99%**
- Overall Steam launch/runtime reconstruction parity:
  **92.45% -> 92.6%**
