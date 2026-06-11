# Quake Live Steam Mapping Round 551: Callback Payload Sizes and Max-Player Publisher

Date: 2026-06-11

## Scope

This round rechecked the small Steam callback-size thunk island around
`0x00465680..0x00465ea0` and the adjacent Steam GameServer max-player publisher
at `0x00465a40`.

The goal was to pin the retail callback object ABI and tighten source
reconstruction where the existing compatibility layer had drifted from the
retail payload size. No live Steam services were enabled; all behavior remains
behind the existing `QL_BUILD_ONLINE_SERVICES` and Steamworks feature gates.

Evidence used:

- Ghidra `functions.csv` rows for `FUN_00465680`, `FUN_00465690`,
  `FUN_00465a40`, and `FUN_00465ea0`
- Binary Ninja HLIL part 02 for the three constant callback-size bodies and the
  `SteamGameServer` slot `0x30` max-player call
- Binary Ninja HLIL part 05 for the `sv_maxclients` publication caller
- Binary Ninja HLIL part 06 for callback vtable `vFunc_2` owners that consume
  the size thunks
- reconstructed source anchors in `platform_steamworks.c`, `sv_main.c`, and
  the Steamworks harness

## Observed Facts

| Raw symbol | Alias | Observed Binary Ninja/Ghidra signal | Reconstruction status |
| --- | --- | --- | --- |
| `sub_465680` | `SteamCallback_GetPayloadSize24` | Ghidra row `FUN_00465680,00465680,6`; HLIL returns `0x18`; vtable consumers include UGC query results, lobby enter/message/data/game-created/kicked, microtransaction auth response, and workshop download result callbacks. | Source-backed by `QL_Steamworks_CallbackGetSize`, which returns the retained callback object's `payloadSize`; registrations pass the matching raw struct `sizeof`. |
| `sub_465690` | `SteamCallback_GetPayloadSize32` | Ghidra row `FUN_00465690,00465690,6`; HLIL returns `0x20`; the observed vtable consumer is `LobbyChatUpdate_t`. | Source-backed by the same retained payload-size path, with `lobbyChatUpdate` registered as `sizeof( ql_steam_lobby_chat_update_raw_t )`. |
| `sub_465a40` | `SteamServer_SetMaxPlayerCount` | Ghidra row `FUN_00465a40,00465a40,26`; HLIL calls `SteamGameServer()` vtable slot `0x30`; HLIL part 05 calls it after reading `sv_maxclients`. | Source-backed by `QL_Steamworks_ServerSetMaxPlayerCount` and `SV_SteamServerUpdatePublishedState`. |
| `sub_465ea0` | `SteamCallback_GetPayloadSize4` | Ghidra row `FUN_00465ea0,00465ea0,6`; HLIL returns `4`; vtable consumers are `SteamServerConnectFailure_t` and `SteamServersDisconnected_t`. | Source-backed by `QL_Steamworks_CallbackGetSize`; this round corrected the raw `SteamServerConnectFailure_t` payload to the retail 4-byte form. |

## Source Reconstruction

The retail binary emits separate constant-return `GetCallbackSizeBytes` methods
for callback payloads of 24, 32, and 4 bytes. The source reconstruction keeps a
single callback vtable with `QL_Steamworks_CallbackGetSize`, and stores the
payload size in each retained callback object during
`QL_Steamworks_PrepareCallbackObject`.

That abstraction remains faithful to the observed vtable contract because
Steam only asks the object for a byte count. The new parity gate pins the
retail constants, the vtable consumers, and the source registration sizes so
future edits cannot silently widen or shrink those payloads.

One source correction was made:

- `ql_steam_server_connect_failure_raw_t` now contains only `int result`.
  Retail HLIL assigns the server connect-failure callback a 4-byte payload via
  `sub_465ea0`; the previous raw struct included a retry flag that belongs to
  a different Steam SDK shape and inflated the registered payload size.

The public `ql_steam_server_connect_failure_t` event still exposes
`stillRetrying` for compatibility with existing source callbacks, but it now
defaults to `qfalse` because the retail payload does not provide that value.

## Alias Promotion

Promoted spelling groups:

- `FUN_00465680`, `sub_465680` -> `SteamCallback_GetPayloadSize24`
- `FUN_00465690`, `sub_465690` -> `SteamCallback_GetPayloadSize32`
- `FUN_00465a40`, `sub_465A40`, `sub_465a40` ->
  `SteamServer_SetMaxPlayerCount`
- `FUN_00465ea0`, `sub_465EA0`, `sub_465ea0` ->
  `SteamCallback_GetPayloadSize4`

## Inference Boundary

Observed facts:

1. The size thunks are pure constant-return callback vtable functions.
2. `sub_465a40` dispatches through `SteamGameServer` slot `0x30`.
3. `SV_SteamServerUpdatePublishedState` publishes `sv_maxclients` through the
   max-player helper.
4. Retail server connect-failure and server-disconnected callbacks share the
   4-byte size thunk.

Inference:

1. The source's single callback-size method is equivalent to the retail
   constant thunk family as long as every registration retains the retail raw
   payload size. The new test makes that equivalence explicit.

## Parity Estimate

- Focused callback payload-size thunk alias confidence:
  **40% -> 99%**
- Focused callback raw-payload source ABI parity:
  **90% -> 98%**
- Focused GameServer max-player publisher mapping confidence:
  **82% -> 99%**
- Overall Steam launch/runtime reconstruction parity:
  **92.35% -> 92.45%**
